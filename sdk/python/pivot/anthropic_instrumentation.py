"""
Anthropic SDK Instrumentation

Auto-instruments Anthropic SDK to emit OpenTelemetry spans with harness.* attributes.
"""

import functools
import hashlib
import json
from typing import Optional
from opentelemetry.trace import Status, StatusCode

from . import tracer, set_harness_attributes, get_current_run_id

_original_create = None
_is_instrumented = False


def instrument_anthropic(
    policy_version: str = "default",
    stakeholder_principal: Optional[str] = None
) -> None:
    """
    Instrument Anthropic SDK with OpenTelemetry.

    Args:
        policy_version: Policy version to record
        stakeholder_principal: Principal making requests

    Example:
        >>> from pivot import instrument_anthropic
        >>> instrument_anthropic(stakeholder_principal="user_alice")
        >>>
        >>> import anthropic
        >>> client = anthropic.Anthropic()
        >>> response = client.messages.create(...)  # Automatically traced
    """
    global _original_create, _is_instrumented

    if _is_instrumented:
        return

    try:
        import anthropic
    except ImportError:
        raise ImportError("anthropic package not installed. Install with: pip install anthropic")

    # Store original method
    _original_create = anthropic.Anthropic.messages.create

    # Wrap with instrumentation
    @functools.wraps(_original_create)
    def instrumented_create(self, *args, **kwargs):
        run_id = get_current_run_id()

        with tracer.start_as_current_span("messages") as span:
            # OTel GenAI core attributes
            span.set_attribute("gen_ai.operation.name", "messages")
            span.set_attribute("gen_ai.request.model", kwargs.get("model", "unknown"))
            span.set_attribute("gen_ai.provider.name", "anthropic")

            # Pivot harness extensions
            set_harness_attributes(
                span,
                run_id=run_id,
                policy_version=policy_version,
                stakeholder_principal=stakeholder_principal
            )

            # Record provenance for replay
            if "temperature" in kwargs:
                span.set_attribute("harness.provenance.temperature", kwargs["temperature"])

            try:
                # Call original method
                response = _original_create(self, *args, **kwargs)

                # Record response metadata
                if hasattr(response, "usage"):
                    span.set_attribute("gen_ai.usage.input_tokens", response.usage.input_tokens)
                    span.set_attribute("gen_ai.usage.output_tokens", response.usage.output_tokens)

                # Compute replay hash
                replay_data = {
                    "model": kwargs.get("model"),
                    "messages": kwargs.get("messages"),
                    "temperature": kwargs.get("temperature"),
                    "max_tokens": kwargs.get("max_tokens"),
                }
                replay_hash = hashlib.sha256(
                    json.dumps(replay_data, sort_keys=True).encode()
                ).hexdigest()[:16]
                span.set_attribute("harness.replay_hash", replay_hash)

                span.set_status(Status(StatusCode.OK))
                return response

            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise

    # Replace method
    anthropic.Anthropic.messages.create = instrumented_create
    _is_instrumented = True


def uninstrument_anthropic() -> None:
    """Remove Anthropic instrumentation."""
    global _original_create, _is_instrumented

    if not _is_instrumented:
        return

    try:
        import anthropic
        if _original_create:
            anthropic.Anthropic.messages.create = _original_create
        _is_instrumented = False
    except ImportError:
        pass
