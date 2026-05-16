# RFC-0003: Policy Schema for Agent Guardrails

**Status:** Draft  
**Author:** Pivot Team  
**Created:** 2026-05-16  
**Updated:** 2026-05-16

---

## Summary

This RFC defines the policy schema for agent guardrails using OPA/Rego with stakeholder graph integration. The schema enables declarative, auditable, and stakeholder-aware policy enforcement for agent reliability.

---

## Motivation

Current guardrail systems have critical limitations:

1. **Content-only rules** - No awareness of who is making the request
2. **Flat allow/deny** - No stakeholder relationships or delegation
3. **Hard to audit** - Imperative code instead of declarative policies
4. **No versioning** - Can't replay with historical policies
5. **Framework-locked** - Tied to specific agent frameworks

The "Agents of Chaos" paper documents 11 failure modes, many caused by **missing stakeholder models** (Cases 2, 5, 7, 8, 10, 11).

We need **stakeholder-aware, declarative, versioned** policies.

---

## Proposal

### Schema Version

```yaml
schema_version: "1.0"
```

### Complete Policy Schema

```yaml
# Policy metadata
name: string                    # Unique policy identifier
version: string                 # Semantic version
description: string             # Human-readable description
author: string                  # Policy author
created: string                 # ISO 8601 timestamp
updated: string                 # ISO 8601 timestamp

# Stakeholder graph
stakeholder_graph:
  principals:
    - id: string                # Unique principal ID
      type: enum                # owner | user | agent | tool | external
      display_name: string      # Human-readable name
      attributes:               # Custom attributes
        role: string
        department: string
        trust_level: enum       # high | medium | low
        
  edges:
    - from: string              # Principal ID
      to: string                # Principal ID
      relation: enum            # owns | delegates_to | peer_of | observes | reports_to
      
  rights:
    - principal: string         # Principal ID or type
      action_class: string      # Action classification
      decision: enum            # allow | ask | deny | ask_with_evidence
      conditions: [string]      # Optional conditions

# Rails (guardrails)
rails:
  # Input rails (fast, <50ms)
  - name: string
    tier: input
    priority: int               # Lower = higher priority
    latency_budget_ms: int      # Max execution time
    enabled: boolean
    async: boolean              # Run asynchronously
    rego_policy: string         # OPA/Rego code
    
  # Tool-call rails
  - name: string
    tier: tool_call
    priority: int
    latency_budget_ms: int
    enabled: boolean
    async: boolean
    rego_policy: string
    
  # Behavioral rails
  - name: string
    tier: behavioral
    priority: int
    latency_budget_ms: int
    enabled: boolean
    async: boolean
    rego_policy: string
    
  # Output rails
  - name: string
    tier: output
    priority: int
    latency_budget_ms: int
    enabled: boolean
    async: boolean
    rego_policy: string
    
  # Multi-agent rails
  - name: string
    tier: multi_agent
    priority: int
    latency_budget_ms: int
    enabled: boolean
    async: boolean
    rego_policy: string

# Action classifications
action_classes:
  - name: string                # e.g., "data_read", "data_write", "data_delete"
    side_effect: enum           # read | write | destructive | external
    reversible: boolean
    blast_radius: enum          # local | tenant | global
    requires_approval: boolean
    
# Budgets and limits
budgets:
  cost:
    max_per_run_usd: float
    max_per_day_usd: float
  tokens:
    max_per_run: int
    max_per_day: int
  time:
    max_per_run_seconds: int
  rate_limits:
    - principal: string
      tool: string
      max_calls_per_minute: int

# Audit configuration
audit:
  log_all_decisions: boolean
  log_denied_only: boolean
  retention_days: int
  export_to_siem: boolean
```

---

## Stakeholder Graph

### Example: Customer Service Agent

```yaml
stakeholder_graph:
  principals:
    - id: owner_alice
      type: owner
      display_name: "Alice (Owner)"
      attributes:
        role: admin
        trust_level: high
        
    - id: user_bob
      type: user
      display_name: "Bob (Customer)"
      attributes:
        role: customer
        trust_level: medium
        
    - id: agent_support
      type: agent
      display_name: "Support Agent"
      attributes:
        role: assistant
        trust_level: high
        
    - id: tool_email
      type: tool
      display_name: "Email Service"
      attributes:
        trust_level: high
        
    - id: external_attacker
      type: external
      display_name: "External Attacker"
      attributes:
        trust_level: low
        
  edges:
    - from: owner_alice
      to: agent_support
      relation: owns
      
    - from: agent_support
      to: tool_email
      relation: delegates_to
      
    - from: user_bob
      to: agent_support
      relation: observes
      
  rights:
    # Owner can do anything
    - principal: owner_alice
      action_class: "*"
      decision: allow
      
    # Users can read their own data
    - principal: user_bob
      action_class: "data_read"
      decision: allow
      conditions: ["data.owner == input.principal"]
      
    # Users cannot write data
    - principal: user_bob
      action_class: "data_write"
      decision: deny
      
    # External principals are denied everything
    - principal: external_attacker
      action_class: "*"
      decision: deny
```

---

## Rail Examples

### 1. PII Detection (Input Rail)

```yaml
rails:
  - name: pii_detector
    tier: input
    priority: 1
    latency_budget_ms: 30
    enabled: true
    async: false
    rego_policy: |
      package pivot.rails.pii_detector
      
      import future.keywords.if
      
      # Detect SSN pattern
      deny[msg] if {
        regex.match(`\d{3}-\d{2}-\d{4}`, input.content)
        msg := "PII detected: SSN pattern found"
      }
      
      # Detect email pattern
      deny[msg] if {
        regex.match(`[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`, input.content)
        input.stakeholder.principal_type != "owner"
        msg := "PII detected: Email found (non-owner)"
      }
```

### 2. Non-Owner Compliance (Tool-Call Rail)

**Solves "Agents of Chaos" Case 2**

```yaml
rails:
  - name: non_owner_compliance
    tier: tool_call
    priority: 2
    latency_budget_ms: 20
    enabled: true
    async: false
    rego_policy: |
      package pivot.rails.non_owner_compliance
      
      import future.keywords.if
      
      # Deny data exfiltration by non-owners
      deny[msg] if {
        input.stakeholder.principal_type != "owner"
        input.tool.side_effect_class == "external"
        input.action_class == "data_export"
        msg := sprintf("Non-owner %s attempted data export", [input.stakeholder.principal])
      }
```

### 3. Irreversibility Detector (Behavioral Rail)

**Solves "Agents of Chaos" Case 1**

```yaml
rails:
  - name: irreversibility_detector
    tier: behavioral
    priority: 3
    latency_budget_ms: 50
    enabled: true
    async: false
    rego_policy: |
      package pivot.rails.irreversibility_detector
      
      import future.keywords.if
      
      # Require owner confirmation for irreversible actions
      ask[msg] if {
        input.tool.reversible == false
        input.tool.blast_radius == "global"
        not owner_confirmed(input)
        msg := sprintf("Irreversible action requires owner confirmation: %s", [input.tool.name])
      }
      
      owner_confirmed(input) if {
        input.metadata.owner_confirmed == true
      }
```

### 4. Cost Budget (Behavioral Rail)

**Solves "Agents of Chaos" Case 4**

```yaml
rails:
  - name: cost_budget
    tier: behavioral
    priority: 4
    latency_budget_ms: 10
    enabled: true
    async: false
    rego_policy: |
      package pivot.rails.cost_budget
      
      import future.keywords.if
      
      deny[msg] if {
        input.run_cost_usd > input.policy.budgets.cost.max_per_run_usd
        msg := sprintf("Cost budget exceeded: $%.2f > $%.2f", 
                       [input.run_cost_usd, input.policy.budgets.cost.max_per_run_usd])
      }
```

### 5. Loop Detection (Behavioral Rail)

**Solves "Agents of Chaos" Case 4**

```yaml
rails:
  - name: loop_detector
    tier: behavioral
    priority: 5
    latency_budget_ms: 30
    enabled: true
    async: false
    rego_policy: |
      package pivot.rails.loop_detector
      
      import future.keywords.if
      
      deny[msg] if {
        action_repetition_count(input.recent_actions, input.current_action) > 3
        msg := "Loop detected: same action repeated >3 times"
      }
      
      action_repetition_count(recent, current) = count if {
        matching := [a | a := recent[_]; a.name == current.name]
        count := count(matching)
      }
```

### 6. Rate Limiting (Tool-Call Rail)

**Solves "Agents of Chaos" Case 5**

```yaml
rails:
  - name: rate_limiter
    tier: tool_call
    priority: 6
    latency_budget_ms: 20
    enabled: true
    async: false
    rego_policy: |
      package pivot.rails.rate_limiter
      
      import future.keywords.if
      
      deny[msg] if {
        limit := get_rate_limit(input.stakeholder.principal, input.tool.name)
        calls_in_window := count_recent_calls(input.stakeholder.principal, input.tool.name, 60)
        calls_in_window >= limit
        msg := sprintf("Rate limit exceeded: %d calls/min (limit: %d)", [calls_in_window, limit])
      }
      
      get_rate_limit(principal, tool) = limit if {
        limit := input.policy.budgets.rate_limits[_]
        limit.principal == principal
        limit.tool == tool
      }
```

---

## Policy Packs

### Pre-built Policy Packs

#### 1. Customer Service Safe

```yaml
name: customer_service_safe
version: "1.0.0"
description: "Safe policies for customer service agents"

rails:
  - pii_detector
  - non_owner_compliance
  - cost_budget
  - rate_limiter
  - output_schema_validator
```

#### 2. Coding Agent Safe

```yaml
name: coding_agent_safe
version: "1.0.0"
description: "Safe policies for coding agents"

rails:
  - irreversibility_detector
  - cost_budget
  - loop_detector
  - secrets_scanner
  - code_injection_detector
```

#### 3. Research Agent Safe

```yaml
name: research_agent_safe
version: "1.0.0"
description: "Safe policies for research agents"

rails:
  - pii_detector
  - cost_budget
  - rate_limiter
  - citation_validator
```

---

## Policy Versioning

Policies are content-addressed:

```
policy_version = sha256(policy_yaml)
```

This enables:
1. **Deterministic replay** - Replay with exact historical policy
2. **A/B testing** - Compare agent behavior under different policies
3. **Audit trail** - Know which policy version was active
4. **Rollback** - Revert to previous policy version

---

## Implementation

### Policy Engine

```go
type PolicyEngine struct {
    opa *rego.Rego
    policy *Policy
}

func (e *PolicyEngine) Evaluate(event Event) Decision {
    // Prepare input
    input := map[string]interface{}{
        "stakeholder": event.Stakeholder,
        "tool": event.Tool,
        "action_class": event.ActionClass,
        "policy": e.policy,
        "recent_actions": event.RecentActions,
    }
    
    // Evaluate all rails in priority order
    for _, rail := range e.policy.Rails {
        if !rail.Enabled {
            continue
        }
        
        decision := e.evaluateRail(rail, input)
        if decision != Allow {
            return decision
        }
    }
    
    return Allow
}
```

### Policy Loading

```python
from pivot.policy import Policy

# Load policy
policy = Policy.from_yaml("policy.yaml")

# Validate
policy.validate()

# Get version
print(policy.version_hash)  # sha256:b4f3a2c1...

# Evaluate
decision = policy.evaluate(event)
```

---

## Alternatives Considered

### 1. Cedar instead of OPA/Rego

**Considered:** Cedar is newer and simpler.

**Decision:** Use OPA as primary, Cedar as secondary. OPA is more mature and widely adopted.

### 2. Imperative Python/Go code

**Rejected:** Not declarative, hard to audit, can't version easily.

### 3. No stakeholder graph

**Rejected:** Can't solve AoC Cases 2, 5, 7, 8, 10, 11 without stakeholder awareness.

---

## Unresolved Questions

1. **Should stakeholder graph be dynamic?**
   - Proposal: Support both static (in policy) and dynamic (from database)
   
2. **How to handle policy conflicts?**
   - Proposal: Priority-based resolution (lower priority number wins)
   
3. **Should we support policy composition?**
   - Proposal: Add `extends: base_policy.yaml` for inheritance

---

## Success Criteria

1. ✅ Can express all 11 AoC failure modes as rails
2. ✅ Stakeholder-aware policy decisions
3. ✅ Content-addressed versioning
4. ✅ <30ms p99 for fast rails
5. ✅ Declarative and auditable
6. ✅ Compatible with OPA/Cedar

---

## References

- [Agents of Chaos Paper](https://arxiv.org/abs/2602.20021)
- [OPA Documentation](https://www.openpolicyagent.org/docs/latest/)
- [Cedar Language](https://www.cedarpolicy.com/)
- [SafeHarness Paper](https://arxiv.org/abs/2604.13630)

---

## Changelog

- **2026-05-16:** Initial draft
