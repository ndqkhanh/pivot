# Phase 1: MVP (Months 3-6)

**Goal:** Build functional MVP with core features across all three pillars

**Status:** 📋 Planned

---

## Overview

Phase 1 delivers a working end-to-end system that demonstrates the unified substrate thesis:
- Python SDK auto-instruments popular agent frameworks
- Gateway enforces policies and stores traces
- Eval engine runs benchmarks with statistical rigor
- Replay engine enables deterministic debugging
- Console UI provides visibility into all three pillars

**Target:** v0.1 release with soft launch to early adopters

---

## Month 3: Python SDK + Gateway Foundation

### Week 9-10: Python SDK Core

**Deliverables:**

#### Auto-Instrumentation
```python
# Target: Zero-code instrumentation
from pivot import instrument_openai, instrument_anthropic

instrument_openai()  # Patches openai.ChatCompletion
instrument_anthropic()  # Patches anthropic.Anthropic

# All LLM calls now emit OTLP spans automatically
```

**Implementation:**
- [ ] OpenAI SDK instrumentation (chat, embeddings, function calling)
- [ ] Anthropic SDK instrumentation (messages, streaming)
- [ ] OTLP span builder with harness.* attributes
- [ ] Context propagation (thread-local + async)
- [ ] Sampling configuration
- [ ] Error handling and retries
- [ ] Performance benchmarking (<2ms overhead)

#### Framework Integrations
- [ ] LangGraph integration (nodes, edges, checkpoints)
- [ ] CrewAI integration (agents, tasks, crews)
- [ ] AutoGen integration (conversable agents)
- [ ] Raw tool call instrumentation

**Testing:**
- [ ] Unit tests for each instrumentation
- [ ] Integration tests with real APIs (mocked)
- [ ] Performance tests (overhead measurement)
- [ ] Example notebooks demonstrating usage

### Week 11-12: Gateway v0

**Deliverables:**

#### OTLP Receiver
```go
// Gateway receives OTLP spans via gRPC and HTTP
type Gateway struct {
    receiver    *otlp.Receiver
    policyEngine *policy.Engine
    storage     *storage.ClickHouse
}
```

**Implementation:**
- [ ] gRPC OTLP receiver
- [ ] HTTP OTLP receiver
- [ ] Span validation and normalization
- [ ] Batch processing and buffering
- [ ] ClickHouse writer with connection pooling
- [ ] Health check and metrics endpoints
- [ ] Graceful shutdown

#### Basic Policy Engine
- [ ] OPA integration
- [ ] Policy loading from files
- [ ] Fast-path evaluation (<30ms p99)
- [ ] Policy decision logging
- [ ] 3 starter policies: PII detection, rate limiting, cost budget

**Testing:**
- [ ] Load testing (10k spans/s)
- [ ] Policy evaluation benchmarks
- [ ] Failure injection tests
- [ ] End-to-end with Python SDK

---

## Month 4: Eval Engine + Storage

### Week 13-14: ClickHouse Schema + Storage Layer

**Deliverables:**

#### Schema Design
```sql
-- Core tables
CREATE TABLE spans (
    trace_id UUID,
    span_id UUID,
    parent_span_id UUID,
    name String,
    kind Enum8('INTERNAL', 'CLIENT', 'SERVER', 'PRODUCER', 'CONSUMER'),
    start_time DateTime64(9),
    end_time DateTime64(9),
    attributes Map(String, String),
    -- harness.* attributes extracted
    run_id String,
    policy_decision String,
    stakeholder_principal String,
    -- Indexes
    INDEX idx_run_id run_id TYPE bloom_filter GRANULARITY 1,
    INDEX idx_trace_id trace_id TYPE bloom_filter GRANULARITY 1
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(start_time)
ORDER BY (start_time, trace_id, span_id);

CREATE TABLE eval_results (
    run_id String,
    task_name String,
    scorer_type String,
    score Float64,
    metadata Map(String, String),
    timestamp DateTime64(9)
) ENGINE = MergeTree()
ORDER BY (task_name, timestamp);
```

**Implementation:**
- [ ] ClickHouse schema migrations
- [ ] Postgres schema for metadata
- [ ] Storage abstraction layer
- [ ] Query builders for common patterns
- [ ] Data retention policies
- [ ] Backup scripts

### Week 15-16: Eval Engine Core

**Deliverables:**

#### Task Runner
```python
# Task execution engine
from pivot.eval import Task, Dataset, Solver, Scorer

task = Task.from_yaml("tasks/tau_bench_retail.yaml")
results = task.run(epochs=8, concurrency=4)
print(results.summary())  # pass@1, pass@4, pass@8, bootstrap CI
```

**Implementation:**
- [ ] YAML task parser
- [ ] Dataset loaders (local, S3, HuggingFace)
- [ ] Solver implementations (ReAct, plan-execute)
- [ ] Scorer implementations:
  - [ ] Exact match
  - [ ] Regex
  - [ ] JSON schema validation
  - [ ] Programmatic (sandboxed Python)
- [ ] Statistical analysis:
  - [ ] Bootstrap confidence intervals
  - [ ] pass^k calculation
  - [ ] McNemar test for paired comparisons
- [ ] Result persistence to ClickHouse

**Benchmark Adapters:**
- [ ] τ-bench retail domain adapter
- [ ] τ-bench airline domain adapter
- [ ] Basic SWE-bench Lite adapter

**Testing:**
- [ ] Unit tests for each scorer
- [ ] Integration tests with real tasks
- [ ] Statistical correctness validation
- [ ] Performance benchmarks

---

## Month 5: Replay Engine + Guardrails

### Week 17-18: Replay Engine v0

**Deliverables:**

#### Deterministic Recording
```python
# Every run records complete provenance
@dataclass
class ReplayRecord:
    run_id: str
    events: List[Event]  # LLM calls, tool calls, observations
    provenance: Provenance  # model fingerprint, seeds, hashes
    
    def replay(self) -> ReplayResult:
        """Deterministically replay this run"""
        pass
```

**Implementation:**
- [ ] Event log schema
- [ ] LLM response caching (keyed by request hash)
- [ ] Tool call recording and replay
- [ ] RNG seed tracking
- [ ] Environment variable capture
- [ ] Sequential replay engine
- [ ] Checkpoint API (save/restore at step N)
- [ ] Replay verification (hash comparison)
- [ ] Determinism rate measurement

**CLI:**
```bash
pivot replay <run_id>                    # Full replay
pivot replay <run_id> --from-step 10     # Checkpoint replay
pivot replay <run_id> --verify           # Verify determinism
```

**Testing:**
- [ ] Replay determinism tests (100 runs)
- [ ] Checkpoint save/restore tests
- [ ] Cache hit/miss scenarios
- [ ] Performance benchmarks

### Week 19-20: Runtime Guardrails

**Deliverables:**

#### 8 Core Rails
1. **Input Rails:**
   - [ ] PII detection (Presidio integration)
   - [ ] Prompt injection detection (PromptGuard-2)

2. **Tool-Call Rails:**
   - [ ] Tool allowlist/denylist
   - [ ] Parameter schema validation
   - [ ] Rate limiting per (tenant, tool)

3. **Behavioral Rails:**
   - [ ] Loop detection (action n-gram repetition)
   - [ ] Cost budget enforcement
   - [ ] Token budget enforcement

4. **Output Rails:**
   - [ ] JSON schema validation

**Implementation:**
- [ ] Rail interface and registry
- [ ] Fast-path evaluation (<30ms p99)
- [ ] Async slow-path evaluation
- [ ] Policy decision logging
- [ ] Circuit breaker for rail failures
- [ ] Rail composition (AND/OR logic)

**OPA Policies:**
```rego
# Example: Cost budget rail
package pivot.rails.cost_budget

import future.keywords.if

deny[msg] if {
    input.run_cost_usd > input.policy.max_cost_usd
    msg := sprintf("Cost budget exceeded: $%.2f > $%.2f", 
                   [input.run_cost_usd, input.policy.max_cost_usd])
}
```

**Testing:**
- [ ] Unit tests for each rail
- [ ] Latency benchmarks
- [ ] Policy composition tests
- [ ] Integration with gateway

---

## Month 6: Console UI + MVP Launch

### Week 21-22: Console UI Foundation

**Deliverables:**

#### Three Core Views

**1. Run Transcript View**
```typescript
// Nested trace visualization
interface RunTranscript {
  runId: string;
  spans: Span[];
  timeline: TimelineEvent[];
  policyDecisions: PolicyDecision[];
}
```

**Implementation:**
- [ ] Next.js app setup
- [ ] ClickHouse query API
- [ ] Span tree visualization (nested)
- [ ] Timeline view with filtering
- [ ] Policy decision annotations
- [ ] LLM request/response viewer
- [ ] Tool call inspector
- [ ] Search and filtering

**2. Replay View**
```typescript
// Time-travel debugging interface
interface ReplayView {
  originalRun: Run;
  replayRun: Run;
  diff: RunDiff;
  checkpoints: Checkpoint[];
}
```

**Implementation:**
- [ ] Replay trigger UI
- [ ] Side-by-side diff view
- [ ] Checkpoint navigation
- [ ] Cache hit/miss indicators
- [ ] Determinism verification display

**3. Eval Dashboard**
```typescript
// Evaluation results and trends
interface EvalDashboard {
  tasks: Task[];
  results: EvalResult[];
  trends: TimeSeries[];
  comparisons: Comparison[];
}
```

**Implementation:**
- [ ] Task list and status
- [ ] Results table with sorting/filtering
- [ ] pass@k visualization
- [ ] Bootstrap CI charts
- [ ] Trend analysis over time
- [ ] A/B comparison view

### Week 23-24: Integration + Launch Prep

**Deliverables:**

#### End-to-End Integration
- [ ] Python SDK → Gateway → ClickHouse → Console
- [ ] Eval engine → Results → Dashboard
- [ ] Replay engine → UI
- [ ] Guardrails → Policy decisions → Transcript

#### Documentation
- [ ] Installation guide
- [ ] Quick start tutorial
- [ ] API reference
- [ ] Example notebooks (5+)
- [ ] Architecture deep-dive
- [ ] Troubleshooting guide

#### Launch Assets
- [ ] 90-second demo video
- [ ] Blog post: "Introducing Pivot"
- [ ] HN post draft
- [ ] Twitter/X thread
- [ ] Reddit r/MachineLearning post

#### Quality Assurance
- [ ] End-to-end test suite
- [ ] Performance benchmarks
- [ ] Security audit (basic)
- [ ] Documentation review
- [ ] User acceptance testing (5 beta users)

---

## Phase 1 Success Metrics

### Technical
- ✅ Python SDK instruments OpenAI/Anthropic/LangGraph/CrewAI
- ✅ Gateway handles 10k spans/s
- ✅ Eval engine runs τ-bench with pass^k
- ✅ Replay achieves ≥95% determinism rate
- ✅ 8 guardrails operational with <30ms p99
- ✅ Console UI displays all three pillars

### Quality
- ✅ 80%+ test coverage
- ✅ All critical paths have integration tests
- ✅ Performance benchmarks documented
- ✅ Security basics in place

### Community
- ✅ v0.1 released on GitHub
- ✅ 10+ external users testing
- ✅ 5+ GitHub issues/PRs from community
- ✅ Positive feedback from beta users

---

## Phase 1 Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Replay determinism <95% | High | Medium | Focus on fingerprint-supporting providers first |
| ClickHouse ops complexity | Medium | Medium | Provide Docker Compose for easy local setup |
| Performance targets missed | High | Low | Continuous benchmarking, optimize hot paths |
| Beta user feedback negative | Medium | Low | Engage early, iterate based on feedback |
| Scope creep | Medium | High | Strict feature freeze after week 20 |

---

## Next Phase Preview

**Phase 2 (M7-12)** will add:
- TypeScript, Java, Go SDKs
- Counterfactual replay operator
- LLM-as-judge scorers with bias mitigation
- Failure clustering + auto-RCA
- GitHub Action for CI integration
- Helm chart for production deployment
- Public benchmarks leaderboard

**Key Milestone:** v1.0 release with production-ready features
