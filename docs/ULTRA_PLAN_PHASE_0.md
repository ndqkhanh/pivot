# Phase 0: Foundation (Months 1-2)

**Goal:** Establish project foundation, finalize architecture, and create core specifications

**Status:** 🔄 In Progress

---

## Week 1-2: Project Bootstrap

### Deliverables

#### 1. Repository Setup
- [x] Create monorepo structure
- [ ] Initialize Git with .gitignore
- [ ] Set up Apache 2.0 LICENSE
- [ ] Create DCO (Developer Certificate of Origin) workflow
- [ ] Set up GitHub Actions CI/CD skeleton
- [ ] Configure branch protection rules

#### 2. Documentation Foundation
- [x] README.md with vision and architecture
- [x] ULTRA_PLAN.md with 18-month roadmap
- [ ] CONTRIBUTING.md with development guidelines
- [ ] CODE_OF_CONDUCT.md
- [ ] SECURITY.md with vulnerability reporting
- [ ] CHANGELOG.md template

#### 3. Development Environment
- [ ] Docker Compose for local development
- [ ] Makefile with common commands
- [ ] Pre-commit hooks (linting, formatting)
- [ ] VS Code workspace settings
- [ ] Development dependencies documentation

### Success Criteria
- ✅ Repository structure matches architecture
- ✅ All core documentation in place
- ✅ Local development environment works
- ✅ CI/CD pipeline runs successfully

---

## Week 3-4: Core Specifications (RFCs)

### RFC-0001: OpenTelemetry Extensions

**Purpose:** Define `harness.*` attribute extensions to OTel GenAI v1.37+

**Key Attributes:**
```yaml
harness.run_id: string           # Unique run identifier
harness.checkpoint_id: string    # Checkpoint identifier for replay
harness.policy_version: string   # Policy version hash
harness.policy_decision: enum    # allow|deny|ask|rewrite|budget_exhausted
harness.replay_hash: string      # Determinism verification hash
harness.stakeholder.principal: string  # Actor principal ID
harness.stakeholder.role: string       # Actor role in stakeholder graph
harness.tool.side_effect_class: enum   # read|write|destructive|external
harness.tool.reversible: boolean       # Can this action be undone?
harness.eval.score: float             # Evaluation score
harness.eval.scorer_type: string      # Scorer that produced this score
harness.failure.cluster_id: string    # Failure cluster assignment
harness.failure.taxonomy: string      # MAST/AoC taxonomy label
```

**Deliverables:**
- [ ] RFC document with full attribute specification
- [ ] JSON Schema for validation
- [ ] Protobuf definitions
- [ ] Example OTLP payloads
- [ ] Contribution to OpenTelemetry GenAI SIG

### RFC-0002: Task Schema

**Purpose:** Define YAML-first evaluation task format

**Schema Structure:**
```yaml
name: string                    # Task identifier
version: string                 # Schema version
dataset:
  type: enum                    # local|remote|synthetic
  source: string                # Path or URL
  format: enum                  # jsonl|csv|parquet
solver:
  type: enum                    # react|plan-execute|custom
  max_steps: int
  timeout_seconds: int
  model: string
  temperature: float
scorers:
  - type: enum                  # exact|regex|json_schema|rubric_judge|...
    config: object
metrics:
  - name: string                # pass@1, pass@4, pass@8, etc.
    aggregation: enum           # mean|median|p95|bootstrap_ci
epochs: int                     # Number of repeated runs
concurrency: int                # Parallel execution
sandbox:
  type: enum                    # gvisor|firecracker|docker
  resources: object
policy:
  name: string                  # Policy pack to apply
  version: string
```

**Deliverables:**
- [ ] RFC document with full schema
- [ ] JSON Schema + YAML schema
- [ ] Compatibility layer with Inspect AI format
- [ ] 10 example tasks (SWE-bench, τ-bench, GAIA, etc.)
- [ ] Validation tooling

### RFC-0003: Policy Schema

**Purpose:** Define OPA/Rego policy format with stakeholder graph

**Schema Structure:**
```yaml
name: string                    # Policy identifier
version: string                 # Semantic version
stakeholder_graph:
  principals:
    - id: string
      type: enum                # owner|user|agent|tool|external
      attributes: object
  edges:
    - from: string
      to: string
      relation: enum            # owns|delegates_to|peer_of|observes
  rights:
    - principal: string
      action_class: string
      decision: enum            # allow|ask|deny|ask_with_evidence
rails:
  - name: string
    tier: enum                  # input|tool_call|behavioral|output|multi_agent
    priority: int
    latency_budget_ms: int
    rego_policy: string         # OPA/Rego code
    async: boolean
```

**Deliverables:**
- [ ] RFC document with full schema
- [ ] JSON Schema for validation
- [ ] 11 policy packs for "Agents of Chaos" cases
- [ ] 14 policy packs for MAST taxonomy
- [ ] Policy testing framework
- [ ] Policy versioning and migration guide

---

## Week 5-6: Architecture Refinement

### System Design Documents

#### 1. Gateway Architecture
- [ ] Component diagram
- [ ] Data flow diagrams
- [ ] API specifications (gRPC + HTTP)
- [ ] Performance requirements
- [ ] Scalability analysis

#### 2. Data Plane Architecture
- [ ] ClickHouse schema design
- [ ] Postgres schema design
- [ ] Redis Streams topology
- [ ] S3 object layout
- [ ] Data retention policies
- [ ] Backup and recovery strategy

#### 3. SDK Architecture
- [ ] Auto-instrumentation strategy
- [ ] Framework integration patterns
- [ ] Context propagation
- [ ] Error handling
- [ ] Performance overhead analysis

#### 4. Security Architecture
- [ ] Threat model
- [ ] Authentication and authorization
- [ ] Data encryption (at rest and in transit)
- [ ] Secrets management
- [ ] Audit logging
- [ ] Compliance considerations (SOC-2, GDPR)

---

## Week 7-8: Prototype & Validation

### Proof of Concept

#### 1. Minimal Gateway
- [ ] OTLP receiver (gRPC)
- [ ] ClickHouse writer
- [ ] Basic policy evaluation (allow/deny)
- [ ] Health check endpoints

#### 2. Python SDK Prototype
- [ ] OpenAI SDK instrumentation
- [ ] OTLP span emission
- [ ] Context propagation
- [ ] Example: instrument a simple agent

#### 3. End-to-End Demo
- [ ] Simple agent (OpenAI + tools)
- [ ] SDK instruments agent
- [ ] Gateway receives and stores traces
- [ ] Query traces from ClickHouse
- [ ] Demonstrate replay of one run

### Validation Criteria
- ✅ Can instrument a real agent
- ✅ Traces appear in ClickHouse
- ✅ Can query and visualize traces
- ✅ Replay produces identical output
- ✅ Performance overhead <10ms per span

---

## Phase 0 Success Metrics

### Documentation
- ✅ 3 RFCs published and reviewed
- ✅ Architecture documents complete
- ✅ Development environment documented

### Technical
- ✅ Proof of concept demonstrates feasibility
- ✅ Performance targets validated
- ✅ Security architecture reviewed

### Community
- ✅ GitHub repository public
- ✅ First external contributors engaged
- ✅ Feedback from 5+ domain experts

---

## Phase 0 Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| OTel GenAI semconv changes | High | Medium | Pin to v1.37+, contribute upstream |
| ClickHouse complexity | Medium | Low | Provide DuckDB fallback for dev |
| RFC feedback delays | Low | Medium | Set 2-week review deadline |
| Proof of concept fails | High | Low | Validate assumptions early with spikes |

---

## Next Phase Preview

**Phase 1 (M3-6)** will focus on:
- Production-quality Python SDK
- Full gateway implementation
- Eval engine with τ-bench support
- Basic replay engine
- 8 core guardrails
- Minimal console UI

**Key Milestone:** v0.1 release with end-to-end functionality
