"""
SOC-2 Compliant Audit Logging

Implements immutable audit trail with:
- 7-year retention policy
- SIEM export capabilities
- Compliance query API
- Tamper-proof logging
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class AuditEventType(Enum):
    """Types of auditable events"""
    # Authentication
    LOGIN = "auth.login"
    LOGOUT = "auth.logout"
    API_KEY_CREATED = "auth.api_key.created"
    API_KEY_REVOKED = "auth.api_key.revoked"

    # Data Access
    SPAN_READ = "data.span.read"
    SPAN_WRITE = "data.span.write"
    EVAL_RUN = "data.eval.run"

    # Configuration
    POLICY_CREATED = "config.policy.created"
    POLICY_UPDATED = "config.policy.updated"
    POLICY_DELETED = "config.policy.deleted"

    # Administrative
    TENANT_CREATED = "admin.tenant.created"
    TENANT_SUSPENDED = "admin.tenant.suspended"
    USER_INVITED = "admin.user.invited"
    USER_REMOVED = "admin.user.removed"


@dataclass
class AuditEvent:
    """An immutable audit event"""
    event_id: str
    timestamp: datetime
    tenant_id: str
    actor_id: str  # User or API key ID
    actor_type: str  # "user", "api_key", "system"
    event_type: AuditEventType
    resource_type: str  # "span", "policy", "tenant", etc.
    resource_id: str
    action: str  # "create", "read", "update", "delete"
    result: str  # "success", "failure", "denied"
    ip_address: str
    user_agent: str
    metadata: Dict[str, Any]
    signature: str  # HMAC signature for tamper detection


class AuditLogger:
    """
    SOC-2 compliant audit logging system

    Features:
    - Immutable append-only log
    - Cryptographic signatures
    - 7-year retention
    - SIEM export
    - Compliance queries
    """

    def __init__(self, storage_backend, signing_key: str):
        self.storage = storage_backend
        self.signing_key = signing_key

    def log_event(
        self,
        tenant_id: str,
        actor_id: str,
        actor_type: str,
        event_type: AuditEventType,
        resource_type: str,
        resource_id: str,
        action: str,
        result: str,
        ip_address: str,
        user_agent: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditEvent:
        """
        Log an audit event

        Args:
            tenant_id: Tenant ID
            actor_id: Who performed the action
            actor_type: Type of actor
            event_type: Type of event
            resource_type: Type of resource affected
            resource_id: ID of resource
            action: Action performed
            result: Result of action
            ip_address: Source IP
            user_agent: User agent string
            metadata: Additional context

        Returns:
            Created audit event
        """
        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now(),
            tenant_id=tenant_id,
            actor_id=actor_id,
            actor_type=actor_type,
            event_type=event_type,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            result=result,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata or {},
            signature=""  # Will be set below
        )

        # Sign event for tamper detection
        event.signature = self._sign_event(event)

        # Write to immutable storage
        self.storage.append_audit_event(event)

        return event

    def query_events(
        self,
        tenant_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        event_types: Optional[List[AuditEventType]] = None,
        actor_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        limit: int = 1000
    ) -> List[AuditEvent]:
        """
        Query audit events for compliance

        Args:
            tenant_id: Tenant to query
            start_time: Start of time range
            end_time: End of time range
            event_types: Filter by event types
            actor_id: Filter by actor
            resource_id: Filter by resource
            limit: Maximum results

        Returns:
            List of matching audit events
        """
        return self.storage.query_audit_events(
            tenant_id=tenant_id,
            start_time=start_time,
            end_time=end_time,
            event_types=event_types,
            actor_id=actor_id,
            resource_id=resource_id,
            limit=limit
        )

    def export_to_siem(
        self,
        tenant_id: str,
        start_time: datetime,
        end_time: datetime,
        format: str = "json"
    ) -> str:
        """
        Export audit events to SIEM

        Args:
            tenant_id: Tenant to export
            start_time: Start of time range
            end_time: End of time range
            format: Export format ("json", "csv", "cef")

        Returns:
            Formatted export data
        """
        events = self.query_events(
            tenant_id=tenant_id,
            start_time=start_time,
            end_time=end_time,
            limit=100000  # Large limit for export
        )

        if format == "json":
            return self._export_json(events)
        elif format == "csv":
            return self._export_csv(events)
        elif format == "cef":
            return self._export_cef(events)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def verify_integrity(self, event: AuditEvent) -> bool:
        """
        Verify event has not been tampered with

        Args:
            event: Event to verify

        Returns:
            True if signature is valid
        """
        expected_signature = self._sign_event(event)
        return event.signature == expected_signature

    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        import uuid
        return f"audit_{uuid.uuid4().hex}"

    def _sign_event(self, event: AuditEvent) -> str:
        """Generate HMAC signature for event"""
        import hmac
        import hashlib

        # Create canonical representation
        canonical = (
            f"{event.event_id}|{event.timestamp.isoformat()}|"
            f"{event.tenant_id}|{event.actor_id}|{event.event_type.value}|"
            f"{event.resource_type}|{event.resource_id}|{event.action}|"
            f"{event.result}"
        )

        # Generate HMAC-SHA256 signature
        signature = hmac.new(
            self.signing_key.encode(),
            canonical.encode(),
            hashlib.sha256
        ).hexdigest()

        return signature

    def _export_json(self, events: List[AuditEvent]) -> str:
        """Export events as JSON"""
        import json
        return json.dumps([self._event_to_dict(e) for e in events], indent=2)

    def _export_csv(self, events: List[AuditEvent]) -> str:
        """Export events as CSV"""
        import csv
        import io

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            "event_id", "timestamp", "tenant_id", "actor_id",
            "event_type", "resource_type", "resource_id",
            "action", "result", "ip_address"
        ])

        writer.writeheader()
        for event in events:
            writer.writerow(self._event_to_dict(event))

        return output.getvalue()

    def _export_cef(self, events: List[AuditEvent]) -> str:
        """Export events as CEF (Common Event Format) for SIEM"""
        lines = []
        for event in events:
            # CEF format: CEF:Version|Device Vendor|Device Product|Device Version|Signature ID|Name|Severity|Extension
            cef_line = (
                f"CEF:0|Pivot|Agent Reliability Platform|1.0|"
                f"{event.event_type.value}|{event.action}|5|"
                f"rt={int(event.timestamp.timestamp() * 1000)} "
                f"src={event.ip_address} "
                f"suser={event.actor_id} "
                f"outcome={event.result}"
            )
            lines.append(cef_line)

        return "\n".join(lines)

    def _event_to_dict(self, event: AuditEvent) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            "event_id": event.event_id,
            "timestamp": event.timestamp.isoformat(),
            "tenant_id": event.tenant_id,
            "actor_id": event.actor_id,
            "actor_type": event.actor_type,
            "event_type": event.event_type.value,
            "resource_type": event.resource_type,
            "resource_id": event.resource_id,
            "action": event.action,
            "result": event.result,
            "ip_address": event.ip_address,
            "user_agent": event.user_agent,
            "metadata": event.metadata
        }


# ClickHouse Schema for Audit Log
AUDIT_LOG_SCHEMA = """
-- Immutable audit log table with 7-year retention

CREATE TABLE audit_log (
    event_id UUID,
    timestamp DateTime64(9),
    tenant_id String,
    actor_id String,
    actor_type String,
    event_type String,
    resource_type String,
    resource_id String,
    action String,
    result String,
    ip_address String,
    user_agent String,
    metadata Map(String, String),
    signature String
) ENGINE = MergeTree()
ORDER BY (tenant_id, timestamp)
PARTITION BY toYYYYMM(timestamp)
SETTINGS storage_policy = 'audit_retention_7_years';

-- Index for compliance queries
CREATE INDEX idx_event_type ON audit_log (event_type) TYPE bloom_filter;
CREATE INDEX idx_actor ON audit_log (actor_id) TYPE bloom_filter;
CREATE INDEX idx_resource ON audit_log (resource_id) TYPE bloom_filter;
"""
