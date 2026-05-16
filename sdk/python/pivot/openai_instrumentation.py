"""
OpenAI SDK Instrumentation

Auto-instruments OpenAI SDK to emit OpenTelemetry spans with harness.* attributes.
"""

import functools
import hashlib
import json
from typing import Any, Dict, Optional
from opentelemetry import trace

from . import tracer, set_harness_attributes, get_current_run_id

_original_create = None
_is_instrumented = False


def instrument_openai(
    policy_version: str = "default",
    stakeholder_principal: Optional[str] = None
) -> None:
    """
    Instrument OpenAI SDK with OpenTelemetry.

    Args:
        policy_version: Policy version to record
        stakeholder_principal: Principal making requests

    Example:
        >>> from pivot import instrument_openai
        >>> instrument_openai(stakeholder_principal="user_alice")
        >>>
        >>> import openai
        >>> response = openai.ChatCompletion.create(...)  # Automatically traced
    """
    global _original_create, _is_instrumented

    if _is_instrumented:
        return

    try:
        import openai
    except ImportError:
        raise ImportError("openai package not installed. Install with: pip install openai")

    # Store original method
    _original_create = openai.ChatCompletion.create

    # Wrap with instrumentation
    @functools.wraps(_original_create)
    def instrumented_create(*args, **kwargs):
        run_id = get_current_run_id()

        with tracer.start_as_current_span("chat") as span:
            # OTel GenAI core attributes
            span.set_attribute("gen_ai.operation.name", "chat")
            span.set_attribute("gen_ai.request.model", kwargs.get("model", "unknown"))
            span.set_attribute("gen_ai.provider.name", "openai")

            # Pivot harness extensions
            set_harness_attributes(
                span,
                run_id=run_id,
                policy_version=policy_version,
                stakeholder_principal=stakeholder_principal
            )

            # Record provenance for replay
            if "seed" in kwargs:
                span.set_attribute("harness.provenance.seed", kwargs["seed"])
            if "temperature" in kwargs:
                span.set_attribute("harness.provenance.temperature", kwargs["temperature"])

            try:
                # Call original method
                response = _original_create(*args, **kwargs)

                # Record response metadata
                if hasattr(response, "system_fingerprint"):
                    span.set_attribute(
                        "harness.provenance.model_fingerprint",
                        response.system_fingerprint
                    )

                if hasattr(response, "usage"):
                    span.set_attribute("gen_ai.usage.input_tokens", response.usage.prompt_tokens)
                    span.set_attribute("gen_ai.usage.output_tokens", response.usage.completion_tokens)

                # Compute replay hash
                replay_data = {
                    "model": kwargs.get("model"),
                    "messages": kwargs.get("messages"),
                    "seed": kwargs.get("seed"),
                    "temperature": kwargs.get("temperature"),
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
    openai.ChatCompletion.create = instrumented_create
    _is_instrumented = True


def uninstrument_openai() -> None:
    """Remove OpenAI instrumentation."""
    global _original_create, _is_instrumented

    if not _is_instrumented:
        return

    try:
        import openai
        if _original_create:
            openai.ChatCompletion.create = _original_create
        _is_instrumented = False
    except ImportError:
        pass
