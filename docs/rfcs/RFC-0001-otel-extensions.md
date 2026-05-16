# RFC-0001: OpenTelemetry Extensions for Agent Reliability

**Status:** Draft  
**Author:** Pivot Team  
**Created:** 2026-05-16  
**Updated:** 2026-05-16

---

## Summary

This RFC defines the `harness.*` attribute extensions to OpenTelemetry GenAI semantic conventions v1.37+ to support agent reliability engineering. These extensions enable deterministic replay, policy enforcement tracking, stakeholder awareness, and failure taxonomy classification.

---

## Motivation

OpenTelemetry GenAI v1.37+ provides excellent foundation for tracing LLM and agent operations, but lacks attributes needed for:

1. **Deterministic Replay** - Provenance information to reproduce runs byte-for-byte
2. **Policy Enforcement** - Tracking which guardrail decisions were made
3. **Stakeholder Awareness** - Recording principal identity for policy evaluation
4. **Failure Classification** - Taxonomizing failures for clustering and analysis
5. **Reliability Metrics** - Computing R(k,ε,λ) reliability surfaces

---

## Proposal

### Namespace

All extensions use the `harness.*` namespace to avoid conflicts with OTel GenAI core attributes.

### Attribute Definitions

#### Core Reliability Attributes

```yaml
harness.run_id:
  type: string
  description: Unique identifier for this agent run (UUID v4)
  requirement: required
  example: "550e8400-e29b-41d4-a716-446655440000"
  
harness.checkpoint_id:
  type: string
  description: Checkpoint identifier for replay fork points
  requirement: optional
  example: "checkpoint_step_47"
  
harness.replay_hash:
  type: string
  description: SHA-256 hash of event for determinism verification
  requirement: optional
  example: "a3c5f8d2e1b4..."
```

#### Policy & Guardrails Attributes

```yaml
harness.policy_version:
  type: string
  description: Content-addressed policy version (SHA-256 of policy)
  requirement: required
  example: "sha256:b4f3a2c1..."
  
harness.policy_decision:
  type: enum
  description: Guardrail decision for this event
  requirement: optional
  values:
    - allow: Action was permitted
    - deny: Action was blocked
    - ask: Human approval requested
    - rewrite: Action was modified
    - budget_exhausted: Resource limit reached
  example: "allow"
  
harness.policy_rail_name:
  type: string
  description: Name of the rail that made the decision
  requirement: optional
  example: "pii_detector"
  
harness.policy_rail_tier:
  type: enum
  description: Rail tier classification
  requirement: optional
  values: [input, tool_call, behavioral, output, multi_agent]
  example: "input"
```

#### Stakeholder Attributes

```yaml
harness.stakeholder.principal:
  type: string
  description: Principal ID from stakeholder graph
  requirement: optional
  example: "user_alice"
  
harness.stakeholder.principal_type:
  type: enum
  description: Type of principal
  requirement: optional
  values: [owner, user, agent, tool, external]
  example: "user"
  
harness.stakeholder.role:
  type: string
  description: Role in stakeholder graph
  requirement: optional
  example: "admin"
```

#### Tool & Action Attributes

```yaml
harness.tool.side_effect_class:
  type: enum
  description: Classification of tool side effects
  requirement: optional
  values:
    - read: Read-only operation
    - write: Modifies state
    - destructive: Irreversible operation
    - external: Calls external service
  example: "write"
  
harness.tool.reversible:
  type: boolean
  description: Whether this action can be undone
  requirement: optional
  example: false
  
harness.tool.blast_radius:
  type: enum
  description: Scope of impact
  requirement: optional
  values: [local, tenant, global]
  example: "tenant"
```

#### Evaluation Attributes

```yaml
harness.eval.score:
  type: float
  description: Evaluation score (0.0 to 1.0)
  requirement: optional
  example: 0.85
  
harness.eval.scorer_type:
  type: string
  description: Type of scorer used
  requirement: optional
  example: "rubric_judge"
  
harness.eval.task_id:
  type: string
  description: Task identifier from eval suite
  requirement: optional
  example: "tau_bench_retail_001"
```

#### Failure & Taxonomy Attributes

```yaml
harness.failure.cluster_id:
  type: string
  description: Failure cluster assignment
  requirement: optional
  example: "cluster_loop_detection_03"
  
harness.failure.taxonomy:
  type: string
  description: Failure classification (MAST or AoC)
  requirement: optional
  example: "aoc_case_04_looping"
  
harness.failure.root_cause:
  type: string
  description: Root cause summary
  requirement: optional
  example: "No budget enforcement"
```

#### Provenance Attributes (for Deterministic Replay)

```yaml
harness.provenance.model_fingerprint:
  type: string
  description: Model system_fingerprint from provider
  requirement: optional
  example: "fp_44709d6fcb"
  
harness.provenance.seed:
  type: integer
  description: Random seed used
  requirement: optional
  example: 42
  
harness.provenance.temperature:
  type: float
  description: Temperature parameter
  requirement: optional
  example: 0.7
  
harness.provenance.tool_io_hash:
  type: string
  description: SHA-256 hash of tool input/output
  requirement: optional
  example: "c5d8f3a2..."
  
harness.provenance.timestamp_recorded:
  type: string
  description: ISO 8601 timestamp when event was recorded
  requirement: optional
  example: "2026-05-16T20:45:00.123Z"
```

---

## Integration with OTel GenAI

### Span Example

```json
{
  "trace_id": "5b8aa5a2d2c872e8321cf37308d69df2",
  "span_id": "051581bf3cb55c13",
  "parent_span_id": "5fb15ad4d3dcf2b2",
  "name": "chat",
  "kind": "CLIENT",
  "start_time": "2026-05-16T20:45:00.000Z",
  "end_time": "2026-05-16T20:45:02.500Z",
  
  "attributes": {
    // OTel GenAI core attributes
    "gen_ai.operation.name": "chat",
    "gen_ai.request.model": "gpt-4",
    "gen_ai.provider.name": "openai",
    "gen_ai.usage.input_tokens": 150,
    "gen_ai.usage.output_tokens": 75,
    
    // Pivot harness extensions
    "harness.run_id": "550e8400-e29b-41d4-a716-446655440000",
    "harness.policy_version": "sha256:b4f3a2c1...",
    "harness.policy_decision": "allow",
    "harness.stakeholder.principal": "user_alice",
    "harness.stakeholder.principal_type": "user",
    "harness.provenance.model_fingerprint": "fp_44709d6fcb",
    "harness.provenance.seed": 42,
    "harness.provenance.temperature": 0.7
  }
}
```

---

## Backwards Compatibility

All `harness.*` attributes are optional and do not conflict with OTel GenAI core attributes. Existing OTel collectors and backends will:
- Accept and store these attributes as custom attributes
- Allow querying via standard OTel query interfaces
- Not break on presence of unknown attributes

---

## Implementation

### SDK Changes

Python SDK example:

```python
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("chat") as span:
    # OTel GenAI core attributes
    span.set_attribute("gen_ai.operation.name", "chat")
    span.set_attribute("gen_ai.request.model", "gpt-4")
    
    # Pivot harness extensions
    span.set_attribute("harness.run_id", run_id)
    span.set_attribute("harness.policy_version", policy_version)
    span.set_attribute("harness.policy_decision", "allow")
    span.set_attribute("harness.stakeholder.principal", principal_id)
    span.set_attribute("harness.provenance.model_fingerprint", fingerprint)
    span.set_attribute("harness.provenance.seed", seed)
```

### Gateway Changes

Gateway extracts `harness.*` attributes for:
- Policy evaluation (stakeholder, tool side effects)
- Replay recording (provenance attributes)
- Failure clustering (taxonomy attributes)

### ClickHouse Schema

```sql
CREATE TABLE spans (
    -- ... standard OTel fields ...
    
    -- Pivot extensions (extracted for performance)
    harness_run_id String,
    harness_checkpoint_id Nullable(String),
    harness_policy_version String,
    harness_policy_decision Enum8('allow'=1, 'deny'=2, 'ask'=3, 'rewrite'=4, 'budget_exhausted'=5),
    harness_stakeholder_principal LowCardinality(String),
    harness_stakeholder_principal_type Enum8('owner'=1, 'user'=2, 'agent'=3, 'tool'=4, 'external'=5),
    harness_replay_hash String,
    
    -- Full attributes map (includes all harness.* attributes)
    attributes Map(String, String),
    
    INDEX idx_run_id harness_run_id TYPE bloom_filter GRANULARITY 1
) ENGINE = MergeTree()
ORDER BY (start_time, trace_id, span_id);
```

---

## Alternatives Considered

### 1. Use OTel Resource Attributes

**Rejected:** Resource attributes are for static metadata (service name, version). Our attributes are per-span and dynamic.

### 2. Use OTel Events

**Rejected:** Events are for discrete occurrences. We need attributes on spans for querying and filtering.

### 3. Custom Namespace (e.g., `pivot.*`)

**Rejected:** `harness.*` is more generic and allows other reliability harnesses to adopt the same conventions.

---

## Unresolved Questions

1. **Should we propose these to OTel GenAI SIG?**
   - Yes, after validation in Pivot v0.1
   - Target: OTel GenAI v1.38+

2. **Should `harness.run_id` be required or optional?**
   - Proposal: Required for Pivot SDK, optional for generic OTel
   - Rationale: Not all OTel users need run-level grouping

3. **Should we version the harness.* schema?**
   - Proposal: Add `harness.schema_version: "1.0"`
   - Rationale: Allows evolution without breaking changes

---

## Success Criteria

1. ✅ All Pivot SDKs emit `harness.*` attributes
2. ✅ Gateway can extract and use attributes for policy decisions
3. ✅ ClickHouse schema supports efficient querying
4. ✅ Replay engine can reconstruct runs from provenance attributes
5. ✅ No conflicts with OTel GenAI core attributes
6. ✅ Backwards compatible with existing OTel infrastructure

---

## References

- [OpenTelemetry GenAI Semantic Conventions v1.37](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- [OpenTelemetry Trace Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/general/trace/)
- [Agents of Chaos Paper](https://arxiv.org/abs/2602.20021)
- [MAST Taxonomy](https://arxiv.org/abs/2503.13657)

---

## Changelog

- **2026-05-16:** Initial draft
