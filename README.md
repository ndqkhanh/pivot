# Pivot - AI Agent Reliability Harness Platform

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Status](https://img.shields.io/badge/Status-Planning-yellow.svg)]()
[![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-v1.37+-green.svg)]()

> **The production-grade reliability harness that makes AI agents measurable, repeatable, and trustworthy.**

Pivot is the first open-source platform that unifies **evaluation**, **runtime guardrails**, and **deterministic replay** into a single OpenTelemetry-native substrate. Built for production, designed for reliability.

---

## 🎯 Vision

Every agent run — in development, in CI, in production — emits a hermetic, replayable record. That record is the unit of truth for:
- **Evaluation:** Does this run pass the rubric?
- **Guardrails:** Which policy fired?
- **Debugging:** Replay step 47, fork to step 50, ask "what if?"

**Reliability becomes a property you measure and enforce, not a property you hope for.**

---

## 🚀 Why Pivot?

### The Problem: Fragmentation

Current tools pick a pillar:
- **Inspect AI** (UK AISI) → Evaluation only
- **Langfuse/Phoenix** → Observability only
- **NeMo Guardrails/LlamaFirewall** → Safety only
- **LangGraph time-travel** → Framework-locked replay

**No tool unifies all three with deterministic replay as a first-class primitive.**

### The Solution: Unified Substrate

Pivot treats reliability as a **unified observable**:
- **Evaluation** = batch query over traces
- **Guardrails** = streaming query over traces
- **Replay** = projection-and-rewrite query over traces

**One log. Three views. Complete reliability loop.**

---

## ✨ Key Features

### 🎯 Evaluation Engine
- **Trace-grounded evaluation:** Production traces become regression tests
- **Statistical rigor:** Bootstrap CIs, pass^k reliability, paired comparisons
- **Benchmark suite:** SWE-bench, τ-bench, GAIA, WebArena, AgentDojo
- **CI integration:** GitHub Action blocks merges on regression

### 🛡️ Runtime Guardrails
- **Five rail tiers:** Input, tool-call, behavioral, output, multi-agent
- **Stakeholder-aware:** Policies parameterized by principal graph
- **Sub-30ms p99:** Fast rails for production inline mode
- **Policy-as-code:** OPA/Rego with versioned, auditable policies

### 🔄 Deterministic Replay
- **Hermetic recording:** Complete LLM requests, tool calls, RNG seeds
- **Three modes:** Sequential, checkpointed, counterfactual
- **Time-travel debugging:** Fork any step, edit state, replay forward
- **Auto-RCA:** AI agent walks trace backward to find root cause

### 📊 Observability
- **OpenTelemetry-native:** GenAI semantic conventions v1.37+
- **ClickHouse backend:** Proven for OTel-at-scale
- **Split-view console:** Run transcript, replay diff, eval dashboard
- **Failure clustering:** 500 failures → 12 buckets with MAST taxonomy

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Agent Application                        │
│                    (LangGraph/CrewAI/etc)                   │
└────────────────────┬────────────────────────────────────────┘
                     │ Harness SDK (Python/TS/Java/Go)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Gateway/Collector (Go)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ OTLP Receiver│  │ Policy Engine│  │ Inline Proxy │     │
│  │              │  │   (OPA/Rego) │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────┬────────────────────────────────────────┘
                     │ OTLP/gRPC
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Plane                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  ClickHouse  │  │   Postgres   │  │Redis Streams │     │
│  │ (Spans/Events)│  │  (Metadata)  │  │ (Live State) │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Eval Engine  │ │Replay Engine │ │  Guardrails  │
│ (Batch Query)│ │(Projection)  │ │(Stream Query)│
└──────────────┘ └──────────────┘ └──────────────┘
        │            │            │
        └────────────┼────────────┘
                     ▼
            ┌──────────────────┐
            │   Console UI     │
            │   (Next.js)      │
            └──────────────────┘
```

---

## 📦 Components

| Component | Language | Purpose |
|-----------|----------|---------|
| **Gateway** | Go | OTLP receiver, policy enforcement, inline proxy |
| **SDK** | Python/TS/Java/Go | Auto-instrumentation for agent frameworks |
| **Eval Engine** | Go + Python | Task runner, scorers, statistical analysis |
| **Replay Engine** | Go | Deterministic replay, counterfactual operator |
| **Policy Engine** | OPA/Rego | Declarative guardrail policies |
| **Sandbox** | gVisor/Firecracker | Isolated execution environments |
| **Console** | Next.js + React | Run transcript, replay UI, eval dashboard |

---

## 🎓 Research Foundation

Pivot is grounded in cutting-edge research:

### Core Papers
- **Agents of Chaos** (arXiv:2602.20021) - 11 documented failure modes
- **MAST** (arXiv:2503.13657) - 14 multi-agent failure taxonomy
- **ReliabilityBench** (arXiv:2601.06112v1) - R(k,ε,λ) reliability surface
- **Agent GPA** (arXiv:2510.08847) - Factorized judges
- **SafeHarness** (arXiv:2604.13630) - Lifecycle-integrated security

### Novel Contributions
1. **Unified substrate:** Three pillars as queries over one log
2. **Counterfactual replay:** Pearl's do-operator for agent traces
3. **Stakeholder graph:** Principal-aware policy parameterization

**Academic paper in preparation for MLSys 2027.**

---

## 🚦 Project Status

**Current Phase:** Planning & Architecture (Month 1-2)

### Roadmap

#### ✅ Phase 0: Foundation (M1-2)
- [x] Research synthesis complete
- [x] Architecture design complete
- [ ] RFC-0001: OTel extensions
- [ ] RFC-0002: Task schema
- [ ] RFC-0003: Policy schema

#### 🔄 Phase 1: MVP (M3-6)
- [ ] Python SDK with OpenAI/Anthropic auto-instrumentation
- [ ] Gateway v0 (OTLP receiver → ClickHouse)
- [ ] Eval engine v0 (τ-bench adapter)
- [ ] Replay engine v0 (sequential replay)
- [ ] 8 built-in guardrails
- [ ] Basic console UI

#### 📋 Phase 2: V1.0 (M7-12)
- [ ] TypeScript/Java/Go SDKs
- [ ] Counterfactual replay
- [ ] Failure clustering + auto-RCA
- [ ] GitHub Action for CI
- [ ] Helm chart + Docker Compose
- [ ] Public benchmarks leaderboard

#### 🎯 Phase 3: Production (M13-18)
- [ ] Multi-tenancy
- [ ] SOC-2 audit log
- [ ] CNCF sandbox application
- [ ] MLSys paper submission

---

## 📚 Documentation

- [**Ultra Plan**](docs/ULTRA_PLAN.md) - Complete 18-month roadmap
- [**Architecture**](docs/architecture/OVERVIEW.md) - System design deep-dive
- [**Research Synthesis**](docs/research/SYNTHESIS.md) - Literature review
- [**RFCs**](docs/rfcs/) - Technical specifications
- [**Benchmarks**](docs/benchmarks/) - Evaluation methodology

---

## 🤝 Contributing

Pivot is in early planning phase. We welcome:
- **Feedback** on architecture and roadmap
- **Research** contributions and paper reviews
- **Design** input on APIs and schemas

**Coming soon:** CONTRIBUTING.md with development setup.

---

## 📄 License

Apache License 2.0 - see [LICENSE](LICENSE)

**DCO (Developer Certificate of Origin) required for contributions.**

---

## 🌟 Acknowledgments

Built on the shoulders of giants:
- **OpenTelemetry** community for GenAI semantic conventions
- **Inspect AI** (UK AISI) for evaluation framework inspiration
- **Langfuse/Phoenix** for observability patterns
- **LlamaFirewall/NeMo Guardrails** for safety primitives
- **Research community** for failure taxonomies and reliability frameworks

---

## 📬 Contact

- **GitHub Issues:** For bugs and feature requests
- **Discussions:** For questions and ideas
- **Email:** [Coming soon]

---

**Pivot: Making AI agents production-ready, one trace at a time.** 🚀
