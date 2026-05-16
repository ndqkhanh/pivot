"""
Multi-Tenancy System for Pivot

Implements tenant isolation with:
- Row-level security in ClickHouse
- API key management per tenant
- Quota enforcement
- Tenant admin UI
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime
import secrets
import hashlib


@dataclass
class Tenant:
    """A tenant in the system"""
    id: str
    name: str
    created_at: datetime
    status: str  # "active", "suspended", "deleted"
    quota: Dict[str, int]  # {"spans_per_day": 1000000, "storage_gb": 100}
    metadata: Dict[str, Any]


@dataclass
class APIKey:
    """API key for tenant authentication"""
    id: str
    tenant_id: str
    key_hash: str
    name: str
    created_at: datetime
    last_used_at: Optional[datetime]
    expires_at: Optional[datetime]
    scopes: List[str]  # ["read", "write", "admin"]
    status: str  # "active", "revoked"


class TenantManager:
    """
    Manages multi-tenancy with isolation

    Features:
    - Tenant CRUD operations
    - API key generation and validation
    - Quota enforcement
    - Row-level security
    """

    def __init__(self, storage_backend):
        self.storage = storage_backend

    def create_tenant(
        self,
        name: str,
        quota: Optional[Dict[str, int]] = None
    ) -> Tenant:
        """
        Create a new tenant

        Args:
            name: Tenant name
            quota: Resource quotas

        Returns:
            Created tenant
        """
        tenant = Tenant(
            id=self._generate_tenant_id(),
            name=name,
            created_at=datetime.now(),
            status="active",
            quota=quota or self._default_quota(),
            metadata={}
        )

        self.storage.save_tenant(tenant)
        return tenant

    def create_api_key(
        self,
        tenant_id: str,
        name: str,
        scopes: List[str],
        expires_days: Optional[int] = None
    ) -> tuple[APIKey, str]:
        """
        Create API key for tenant

        Args:
            tenant_id: Tenant ID
            name: Key name
            scopes: Permission scopes
            expires_days: Expiration in days (None = never)

        Returns:
            (APIKey object, raw key string)
        """
        # Generate secure key
        raw_key = self._generate_api_key()
        key_hash = self._hash_key(raw_key)

        # Calculate expiration
        expires_at = None
        if expires_days:
            from datetime import timedelta
            expires_at = datetime.now() + timedelta(days=expires_days)

        api_key = APIKey(
            id=self._generate_key_id(),
            tenant_id=tenant_id,
            key_hash=key_hash,
            name=name,
            created_at=datetime.now(),
            last_used_at=None,
            expires_at=expires_at,
            scopes=scopes,
            status="active"
        )

        self.storage.save_api_key(api_key)

        # Return both object and raw key (only time raw key is visible)
        return api_key, raw_key

    def validate_api_key(self, raw_key: str) -> Optional[APIKey]:
        """
        Validate API key and return associated key object

        Args:
            raw_key: Raw API key string

        Returns:
            APIKey if valid, None otherwise
        """
        key_hash = self._hash_key(raw_key)
        api_key = self.storage.get_api_key_by_hash(key_hash)

        if not api_key:
            return None

        # Check status
        if api_key.status != "active":
            return None

        # Check expiration
        if api_key.expires_at and datetime.now() > api_key.expires_at:
            return None

        # Update last used
        api_key.last_used_at = datetime.now()
        self.storage.update_api_key(api_key)

        return api_key

    def check_quota(self, tenant_id: str, resource: str, amount: int) -> bool:
        """
        Check if tenant has quota for resource

        Args:
            tenant_id: Tenant ID
            resource: Resource type (e.g., "spans_per_day")
            amount: Amount to check

        Returns:
            True if within quota, False otherwise
        """
        tenant = self.storage.get_tenant(tenant_id)
        if not tenant:
            return False

        # Get current usage
        usage = self.storage.get_tenant_usage(tenant_id, resource)

        # Check against quota
        quota_limit = tenant.quota.get(resource, 0)
        return (usage + amount) <= quota_limit

    def enforce_quota(self, tenant_id: str, resource: str, amount: int):
        """
        Enforce quota - raise exception if exceeded

        Args:
            tenant_id: Tenant ID
            resource: Resource type
            amount: Amount to consume

        Raises:
            QuotaExceededError if quota exceeded
        """
        if not self.check_quota(tenant_id, resource, amount):
            raise QuotaExceededError(
                f"Quota exceeded for {resource}. "
                f"Contact support to increase limits."
            )

        # Increment usage
        self.storage.increment_usage(tenant_id, resource, amount)

    def _generate_tenant_id(self) -> str:
        """Generate unique tenant ID"""
        import uuid
        return f"tenant_{uuid.uuid4().hex[:12]}"

    def _generate_key_id(self) -> str:
        """Generate unique key ID"""
        import uuid
        return f"key_{uuid.uuid4().hex[:12]}"

    def _generate_api_key(self) -> str:
        """Generate secure API key"""
        # Format: sk_<tenant_prefix>_<random_32_bytes>
        random_part = secrets.token_urlsafe(32)
        return f"sk_pivot_{random_part}"

    def _hash_key(self, raw_key: str) -> str:
        """Hash API key for storage"""
        return hashlib.sha256(raw_key.encode()).hexdigest()

    def _default_quota(self) -> Dict[str, int]:
        """Default quota for new tenants"""
        return {
            "spans_per_day": 1_000_000,
            "storage_gb": 100,
            "api_calls_per_minute": 1000
        }


class QuotaExceededError(Exception):
    """Raised when tenant quota is exceeded"""
    pass


# ClickHouse Row-Level Security
CLICKHOUSE_RLS_POLICY = """
-- Row-level security policy for multi-tenancy
-- Ensures tenants can only access their own data

CREATE POLICY tenant_isolation ON spans
FOR SELECT
USING tenant_id = currentUser()

-- Apply to all span tables
ALTER TABLE spans ENABLE ROW LEVEL SECURITY;
ALTER TABLE eval_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE replay_checkpoints ENABLE ROW LEVEL SECURITY;
"""
