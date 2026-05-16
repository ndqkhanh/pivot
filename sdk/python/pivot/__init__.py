"""
Pivot Python SDK - Core Module

Auto-instrumentation for OpenAI and Anthropic with OpenTelemetry integration.
"""

from typing import Optional
import uuid
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

__version__ = "0.1.0"

# Global tracer
tracer = trace.get_tracer(__name__, __version__)


class PivotConfig:
    """Configuration for Pivot SDK."""

    def __init__(
        self,
        endpoint: str = "http://localhost:4317",
        run_id: Optional[str] = None,
        policy_version: Optional[str] = None,
        stakeholder_principal: Optional[str] = None,
        enable_replay: bool = True,
    ):
        self.endpoint = endpoint
        self.run_id = run_id or str(uuid.uuid4())
        self.policy_version = policy_version or "default"
        self.stakeholder_principal = stakeholder_principal or "unknown"
        self.enable_replay = enable_replay


def initialize(config: Optional[PivotConfig] = None) -> PivotConfig:
    """
    Initialize Pivot SDK with OpenTelemetry.

    Args:
        config: Optional configuration. If None, uses defaults.

    Returns:
        The configuration used.

    Example:
        >>> from pivot import initialize
        >>> config = initialize()
        >>> print(config.run_id)
    """
    if config is None:
        config = PivotConfig()

    # Set up OpenTelemetry
    provider = TracerProvider()
    processor = BatchSpanProcessor(
        OTLPSpanExporter(endpoint=config.endpoint)
    )
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

    return config


def get_current_run_id() -> str:
    """Get the current run ID."""
    # This would be stored in context in real implementation
    return str(uuid.uuid4())


def set_harness_attributes(
    span: trace.Span,
    run_id: str,
    policy_version: str,
    stakeholder_principal: Optional[str] = None,
    **kwargs
) -> None:
    """
    Set harness.* attributes on a span.

    Args:
        span: OpenTelemetry span
        run_id: Unique run identifier
        policy_version: Policy version hash
        stakeholder_principal: Principal ID
        **kwargs: Additional harness attributes
    """
    span.set_attribute("harness.run_id", run_id)
    span.set_attribute("harness.policy_version", policy_version)

    if stakeholder_principal:
        span.set_attribute("harness.stakeholder.principal", stakeholder_principal)

    for key, value in kwargs.items():
        if key.startswith("harness."):
            span.set_attribute(key, value)


# Re-export for convenience
__all__ = [
    "initialize",
    "PivotConfig",
    "tracer",
    "get_current_run_id",
    "set_harness_attributes",
    "Status",
    "StatusCode",
]
