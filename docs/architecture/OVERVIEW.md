# Pivot Architecture Overview

**Version:** 1.0  
**Date:** 2026-05-16  
**Status:** Design Phase

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Core Principles](#core-principles)
3. [Component Architecture](#component-architecture)
4. [Data Flow](#data-flow)
5. [Deployment Models](#deployment-models)
6. [Performance Characteristics](#performance-characteristics)
7. [Security Architecture](#security-architecture)

---

## System Overview

Pivot is a distributed system for agent reliability engineering, built around a single unified trace substrate. The architecture follows a **control plane / data plane** separation pattern common in cloud-native infrastructure.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Agent Applications                        │
│  (LangGraph, CrewAI, AutoGen, Custom Agents)                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Pivot SDK (Python/TS/Java/Go)
                         │ Auto-instrumentation + OTLP Export
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Control Plane (Go)                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Gateway/Collector                      │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │  │
│  │  │OTLP Receiver│  │Policy Engine│  │Inline Proxy │     │  │
│  │  │ (gRPC/HTTP) │  │  (OPA/Rego) │  │  (Optional) │     │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘     │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ OTLP/gRPC + Policy Decisions
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Data Plane                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  ClickHouse  │  │   Postgres   │  │Redis Streams │         │
│  │              │  │              │  │              │         │
│  │ Spans/Events │  │   Metadata   │  │  Live State  │         │
│  │   Metrics    │  │   Policies   │  │   Queues     │         │
│  │              │  │   Datasets   │  │              │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    S3-Compatible Storage                  │  │
│  │         (Large Payloads, Artifacts, Checkpoints)         │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Query APIs
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Query Engines                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Eval Engine  │  │Replay Engine │  │  Guardrails  │         │
│  │              │  │              │  │              │         │
│  │ Batch Query  │  │ Projection   │  │Stream Query  │         │
│  │ (Go+Python)  │  │    (Go)      │  │    (Go)      │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ REST/GraphQL APIs
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Presentation Layer                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   Console UI (Next.js)                    │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │  │
│  │  │   Run       │  │   Replay    │  │    Eval     │     │  │
│  │  │ Transcript  │  │  Time-Travel│  │  Dashboard  │     │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘     │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Principles

### 1. Unified Substrate

**Thesis:** Evaluation, guardrails, and replay are three queries over the same typed trace substrate.

```
Trace = DAG of Events
Event = (id, parent_id, timestamp, actor, kind, payload, provenance)

Evaluation  = Batch Query(Trace, Spec) → Score
Guardrails  = Stream Query(Event, Policy) → Decision
Replay      = Projection(Trace, Intervention) → Trace'
```

### 2. Deterministic Replay Contract

Every event carries provenance sufficient for deterministic replay:

```
σ_provenance = {
  model_fingerprint: string,
  seed: int,
  temperature: float,
  tool_io_hash: string,
  policy_version: string,
  timestamp: datetime,
  env_vars: map[string]string
}
```

**Replay Guarantee:** If σ is preserved and model honors fingerprint, replay is byte-identical.

### 3. Stakeholder-Aware Policies

Policies are parameterized by a stakeholder graph:

```
S = (Principals, Edges, Rights)

Principals = {owner, user, agent, tool, external}
Edges = {owns, delegates_to, peer_of, observes}
Rights = Principal × ActionClass → {allow, ask, deny}

Rail(event, S) → Decision
```

### 4. OpenTelemetry-Native

All instrumentation uses OTel GenAI semantic conventions v1.37+. This ensures:
- Vendor neutrality
- Ecosystem compatibility
- Future-proofing

### 5. Production-Grade Performance

**Targets:**
- SDK overhead: <2ms per span
- Gateway latency: <30ms p99 (fast rails)
- Throughput: 50k events/s per gateway node
- Replay determinism: ≥99.5%

---

## Component Architecture

### 1. SDK Layer

**Purpose:** Auto-instrument agent frameworks and emit OTLP spans.

**Languages:** Python (primary), TypeScript, Java, Go

**Architecture:**

```python
# Python SDK Architecture
pivot/
├── instrumentation/
│   ├── openai.py          # Patch openai.ChatCompletion
│   ├── anthropic.py       # Patch anthropic.Anthropic
│   ├── langchain.py       # Hook LangChain callbacks
│   ├── langgraph.py       # Hook LangGraph nodes
│   └── crewai.py          # Hook CrewAI agents
├── tracing/
│   ├── span_builder.py    # Build OTel spans
│   ├── context.py         # Context propagation
│   └── sampler.py         # Sampling logic
├── exporter/
│   ├── otlp_grpc.py       # gRPC exporter
│   └── otlp_http.py       # HTTP exporter
└── config.py              # Configuration
```

**Key Features:**
- Zero-code instrumentation (import and call `instrument_*()`)
- Automatic context propagation (thread-local + async)
- Configurable sampling
- Batch export for performance
- Graceful degradation on errors

### 2. Gateway/Collector

**Purpose:** Receive OTLP spans, enforce policies, persist to data plane.

**Language:** Go (for performance and operational simplicity)

**Architecture:**

```
gateway/
├── cmd/
│   └── gateway/
│       └── main.go
├── internal/
│   ├── receiver/
│   │   ├── otlp_grpc.go
│   │   └── otlp_http.go
│   ├── policy/
│   │   ├── engine.go       # OPA integration
│   │   ├── loader.go       # Policy loading
│   │   └── cache.go        # Decision caching
│   ├── storage/
│   │   ├── clickhouse.go
│   │   ├── postgres.go
│   │   └── redis.go
│   ├── proxy/
│   │   └── inline.go       # Optional inline proxy
│   └── metrics/
│       └── prometheus.go
└── pkg/
    ├── span/
    │   ├── validator.go
    │   └── normalizer.go
    └── batch/
        └── processor.go
```

**Modes:**

**1. OTLP Receiver Mode (Default):**
```
Agent → SDK → OTLP → Gateway → ClickHouse
```

**2. Inline Proxy Mode (Optional):**
```
Agent → Gateway (proxy) → LLM API
                ↓
         Policy Enforcement
                ↓
           ClickHouse
```

**Performance:**
- Async policy evaluation for slow rails
- Batch writes to ClickHouse (1000 spans/batch)
- Connection pooling
- Circuit breakers for downstream failures

### 3. Data Plane

#### ClickHouse (Spans & Events)

**Schema:**

```sql
CREATE TABLE spans (
    trace_id UUID,
    span_id UUID,
    parent_span_id Nullable(UUID),
    name LowCardinality(String),
    kind Enum8('INTERNAL'=1, 'CLIENT'=2, 'SERVER'=3, 'PRODUCER'=4, 'CONSUMER'=5),
    start_time DateTime64(9),
    end_time DateTime64(9),
    duration_ns UInt64,
    
    -- OTel GenAI attributes
    gen_ai_operation_name LowCardinality(String),
    gen_ai_request_model LowCardinality(String),
    gen_ai_provider_name LowCardinality(String),
    gen_ai_usage_input_tokens UInt32,
    gen_ai_usage_output_tokens UInt32,
    
    -- Pivot extensions
    harness_run_id String,
    harness_checkpoint_id Nullable(String),
    harness_policy_version String,
    harness_policy_decision Enum8('allow'=1, 'deny'=2, 'ask'=3, 'rewrite'=4),
    harness_stakeholder_principal LowCardinality(String),
    harness_replay_hash String,
    
    -- Full attributes as Map
    attributes Map(String, String),
    
    -- Indexes
    INDEX idx_run_id harness_run_id TYPE bloom_filter GRANULARITY 1,
    INDEX idx_trace_id trace_id TYPE bloom_filter GRANULARITY 1,
    INDEX idx_model gen_ai_request_model TYPE set(0) GRANULARITY 1
    
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(start_time)
ORDER BY (start_time, trace_id, span_id)
SETTINGS index_granularity = 8192;
```

**Materialized Views:**

```sql
-- Aggregated metrics
CREATE MATERIALIZED VIEW span_metrics_hourly
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMMDD(hour)
ORDER BY (hour, gen_ai_request_model, harness_policy_decision)
AS SELECT
    toStartOfHour(start_time) AS hour,
    gen_ai_request_model,
    harness_policy_decision,
    count() AS span_count,
    sum(gen_ai_usage_input_tokens) AS total_input_tokens,
    sum(gen_ai_usage_output_tokens) AS total_output_tokens,
    avg(duration_ns) AS avg_duration_ns
FROM spans
GROUP BY hour, gen_ai_request_model, harness_policy_decision;
```

#### Postgres (Metadata)

**Schema:**

```sql
-- Projects/Tenants
CREATE TABLE projects (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    settings JSONB
);

-- Datasets
CREATE TABLE datasets (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    name VARCHAR(255) NOT NULL,
    format VARCHAR(50),
    source_url TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Tasks
CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    name VARCHAR(255) NOT NULL,
    dataset_id UUID REFERENCES datasets(id),
    config JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Policies
CREATE TABLE policies (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    name VARCHAR(255) NOT NULL,
    version VARCHAR(50) NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    rego_code TEXT NOT NULL,
    stakeholder_graph JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(project_id, name, version)
);

-- Eval Results
CREATE TABLE eval_results (
    id UUID PRIMARY KEY,
    task_id UUID REFERENCES tasks(id),
    run_id VARCHAR(255) NOT NULL,
    score FLOAT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

#### Redis Streams (Live State)

**Purpose:** Low-latency queues for policy decisions and live updates.

**Streams:**

```
pivot:policy:decisions     # Policy decision events
pivot:eval:jobs            # Eval job queue
pivot:replay:requests      # Replay request queue
pivot:alerts               # Alert notifications
```

#### S3 (Large Payloads)

**Structure:**

```
s3://pivot-data/
├── spans/
│   └── {project_id}/
│       └── {date}/
│           └── {trace_id}.json.gz
├── checkpoints/
│   └── {run_id}/
│       └── step_{n}.json.gz
├── artifacts/
│   └── {run_id}/
│       └── {artifact_id}
└── datasets/
    └── {dataset_id}/
        └── data.jsonl.gz
```

---

## Data Flow

### 1. Instrumentation Flow

```
┌─────────────┐
│Agent calls  │
│LLM API      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│SDK intercepts│
│and wraps    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Build OTel   │
│span with    │
│harness.*    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Batch export │
│via OTLP     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Gateway      │
│receives     │
└─────────────┘
```

### 2. Policy Enforcement Flow

```
┌─────────────┐
│Span arrives │
│at Gateway   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Extract      │
│policy attrs │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Fast rails   │
│(<30ms)      │
└──────┬──────┘
       │
       ├─ allow ──────────┐
       ├─ deny ───────────┤
       └─ ask ────────────┤
                          │
                          ▼
                   ┌─────────────┐
                   │Slow rails   │
                   │(async)      │
                   └──────┬──────┘
                          │
                          ▼
                   ┌─────────────┐
                   │Log decision │
                   │to ClickHouse│
                   └─────────────┘
```

### 3. Evaluation Flow

```
┌─────────────┐
│Load task    │
│from YAML    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Load dataset │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│For each     │
│sample, run  │
│solver       │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Collect      │
│traces       │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Apply scorers│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Aggregate    │
│metrics      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Store results│
│to Postgres  │
└─────────────┘
```

### 4. Replay Flow

```
┌─────────────┐
│Load run     │
│from         │
│ClickHouse   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Extract event│
│log with     │
│provenance   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│For each     │
│event:       │
│- LLM: cache │
│- Tool: cache│
│- RNG: seed  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Verify hash  │
│matches      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Return replay│
│result +     │
│determinism  │
│rate         │
└─────────────┘
```

---

## Deployment Models

### 1. Local Development

```bash
docker-compose up -d
# Includes: gateway, clickhouse, postgres, redis, console
```

**Use Case:** Local testing, development

### 2. Single-Node Production

```bash
# Docker Compose with persistent volumes
docker-compose -f docker-compose.prod.yml up -d
```

**Use Case:** Small teams, <10k spans/day

### 3. Kubernetes (Helm)

```bash
helm install pivot pivot/pivot \
  --set clickhouse.replicas=3 \
  --set gateway.replicas=5
```

**Use Case:** Medium to large teams, >10k spans/day

### 4. Multi-Region

```yaml
regions:
  - us-east-1: {gateway: 10, clickhouse: 3}
  - eu-west-1: {gateway: 5, clickhouse: 3}
  - ap-southeast-1: {gateway: 3, clickhouse: 3}
```

**Use Case:** Global enterprises, compliance requirements

---

## Performance Characteristics

### Latency

| Component | p50 | p95 | p99 |
|-----------|-----|-----|-----|
| SDK overhead | <1ms | <2ms | <5ms |
| Gateway (fast rails) | <10ms | <20ms | <30ms |
| Gateway (slow rails) | 200ms | 500ms | 800ms |
| ClickHouse write | <5ms | <10ms | <20ms |
| ClickHouse query (simple) | <50ms | <100ms | <200ms |
| Replay (100 steps) | <2s | <5s | <10s |

### Throughput

| Component | Target | Tested |
|-----------|--------|--------|
| Gateway | 50k spans/s/node | TBD |
| ClickHouse | 1M rows/s | TBD |
| SDK export | 10k spans/s | TBD |

### Storage

| Data Type | Compression | Retention |
|-----------|-------------|-----------|
| Spans | ~85% (ClickHouse) | 90 days default |
| Eval results | ~70% | 1 year |
| Audit logs | ~60% | 7 years |
| Artifacts | ~50% (gzip) | 30 days |

---

## Security Architecture

### 1. Authentication

- API keys (project-scoped)
- OAuth 2.0 / OIDC (enterprise)
- SAML 2.0 (enterprise)

### 2. Authorization

- RBAC (role-based access control)
- Resource-level permissions
- Tenant isolation

### 3. Encryption

- TLS 1.3 for all network traffic
- At-rest encryption (ClickHouse, S3)
- Secrets management (Vault integration)

### 4. Audit

- Immutable audit log
- All API calls logged
- Compliance exports (SIEM)

---

## Next Steps

1. **RFC-0001:** Finalize OTel attribute extensions
2. **RFC-0002:** Finalize task schema
3. **RFC-0003:** Finalize policy schema
4. **Proof of Concept:** Build minimal end-to-end system
5. **Performance Validation:** Benchmark against targets

---

**See Also:**
- [Ultra Plan](../ULTRA_PLAN.md)
- [Research Synthesis](../research/SYNTHESIS.md)
- [RFCs](../rfcs/)
