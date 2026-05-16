# Pivot Guardrails - OPA Policy Pack

Production-ready guardrails for agent safety and reliability.

## Overview

8 core guardrails implementing the "Agents of Chaos" safety patterns:

1. **PII Detection** - Prevent sensitive data leakage
2. **Cost Budget** - Enforce spending limits
3. **Loop Detection** - Prevent infinite loops
4. **Rate Limiting** - Control API usage
5. **Irreversibility Detector** - Require confirmation for destructive actions
6. **Non-Owner Compliance** - Stakeholder-aware permissions
7. **Output Schema Validation** - Ensure correct output format
8. **Prompt Injection Detection** - Block malicious inputs

## Quick Start

```bash
# Start OPA server
opa run --server policy-pack/

# Test policy
opa eval -d policy-pack/ -i input.json "data.pivot.rails.pii_detector.deny"
```

## Policy Structure

```
policy-pack/
├── rails/
│   ├── pii_detector.rego
│   ├── cost_budget.rego
│   ├── loop_detector.rego
│   ├── rate_limiter.rego
│   ├── irreversibility_detector.rego
│   ├── non_owner_compliance.rego
│   ├── output_validator.rego
│   └── prompt_injection.rego
└── tests/
    └── rails_test.rego
```

## Example Policy

```rego
package pivot.rails.pii_detector

import future.keywords.if

# Deny if SSN pattern detected
deny[msg] if {
    regex.match(`\d{3}-\d{2}-\d{4}`, input.content)
    msg := "PII detected: SSN pattern found"
}
```

## Integration

Policies are evaluated by the Gateway before span ingestion:

```
Span → Gateway → OPA Policy → Allow/Deny → ClickHouse
```

## Performance

- **Latency**: <30ms p99 for fast rails
- **Throughput**: 50k decisions/s
- **Caching**: Decision caching for repeated patterns

## License

Apache 2.0
