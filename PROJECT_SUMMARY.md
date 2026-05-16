# Pivot Project Summary

**Created:** 2026-05-16  
**Status:** Planning Phase  
**Repository:** https://github.com/pivot-ai/pivot (to be created)

---

## 🎯 Project Overview

**Pivot** is the world's first production-grade, open-source AI Agent Reliability Harness Platform that unifies **evaluation**, **runtime guardrails**, and **deterministic replay** into a single OpenTelemetry-native substrate.

### The Problem

Current agent reliability tools are fragmented:
- **Inspect AI** → Evaluation only
- **Langfuse/Phoenix** → Observability only
- **NeMo Guardrails/LlamaFirewall** → Safety only
- **LangGraph time-travel** → Framework-locked replay

**No tool unifies all three with deterministic replay as a first-class primitive.**

### The Solution

Pivot treats reliability as a **unified observable**:
```
Evaluation  = Batch Query(Trace, Spec) → Score
Guardrails  = Stream Query(Event, Policy) → Decision
Replay      = Projection(Trace, Intervention) → Trace'
```

**One log. Three views. Complete reliability loop.**

---

## 📊 Research Foundation

### Key Papers Synthesized

1. **Agents of Chaos** (arXiv:2602.20021) - 11 documented failure modes
2. **MAST** (arXiv:2503.13657) - 14 multi-agent failure taxonomy
3. **ReliabilityBench** (arXiv:2601.06112v1) - R(k,ε,λ) reliability surface
4. **Agent GPA** (arXiv:2510.08847) - Factorized judges
5. **SafeHarness** (arXiv:2604.13630) - Lifecycle-integrated security
6. **Agentic Benchmark Checklist** (arXiv:2507.02825) - Validity framework

**Total:** 50+ papers, 40+ GitHub repositories analyzed

### Novel Contributions

1. **Unified Substrate:** Three pillars as queries over one log
2. **Counterfactual Replay:** Pearl's do-operator for agent traces
3. **Stakeholder Graph:** Principal-aware policy parameterization
4. **Trace-Grounded Evaluation:** Production traces as regression tests

---

## 🏗️ Architecture

### System Components

```
Agent Apps (LangGraph/CrewAI/etc)
    ↓
SDK (Python/TS/Java/Go) - Auto-instrumentation
    ↓
Gateway (Go) - OTLP receiver + Policy engine
    ↓
Data Plane (ClickHouse + Postgres + Redis + S3)
    ↓
Query Engines (Eval + Replay + Guardrails)
    ↓
Console UI (Next.js) - Run transcript + Replay + Eval dashboard
```

### Tech Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Control Plane | Go | Performance, single binary |
| Primary SDK | Python | ML ecosystem fit |
| Secondary SDKs | TypeScript, Java, Go | Ecosystem coverage |
| Trace Store | ClickHouse | Proven for OTel-at-scale |
| Metadata | Postgres + pgvector | Standard + embeddings |
| Live State | Redis Streams | Low-latency queues |
| Object Store | S3-compatible | Large payloads |
| Policy | OPA/Rego | Declarative, auditable |
| Sandbox | gVisor/Firecracker | Speed vs isolation |
| UI | Next.js + React | Standard ecosystem |

---

## 📅 18-Month Roadmap

### Phase 0: Foundation (M1-2) ✅ Current Phase

**Deliverables:**
- [x] Repository structure created
- [x] Ultra plan documented
- [x] Research synthesis complete
- [x] Architecture designed
- [ ] RFC-0001: OTel extensions
- [ ] RFC-0002: Task schema
- [ ] RFC-0003: Policy schema
- [ ] Proof of concept

**Timeline:** Weeks 1-8

### Phase 1: MVP (M3-6)

**Deliverables:**
- Python SDK (OpenAI, Anthropic, LangGraph, CrewAI)
- Gateway v0 (OTLP receiver + ClickHouse)
- Eval engine v0 (τ-bench adapter)
- Replay engine v0 (sequential replay)
- 8 core guardrails
- Basic console UI
- **v0.1 Release**

**Timeline:** Weeks 9-24

### Phase 2: V1.0 (M7-12)

**Deliverables:**
- TypeScript, Java, Go SDKs
- Counterfactual replay operator
- LLM-as-judge with bias mitigation
- Failure clustering + auto-RCA
- GitHub Action for CI
- Helm chart + Docker Compose
- Public benchmarks leaderboard
- **v1.0 Release**

**Timeline:** Weeks 25-48

### Phase 3: Production Hardening (M13-18)

**Deliverables:**
- MLSys paper submission
- CNCF sandbox application
- Multi-region deployment
- Enterprise features (SSO, RBAC, SOC-2)
- Community governance maturation
- **Industry Standard Status**

**Timeline:** Weeks 49-72

---

## 🎓 Academic Contribution

### Paper Title

*"Pivot: A Unified Trace Substrate for Agent Reliability — Evaluation, Guardrails, and Counterfactual Replay as Queries on One Log"*

### Target Venue

**Primary:** MLSys 2027  
**Secondary:** COLM 2027

### Core Scientific Claim

> Evaluation, runtime guardrails, and failure analysis are not separate concerns — they are three queries (batch, streaming, projection-and-rewrite) over the same typed trace algebra. Unifying them enables a "reliability loop" where production guardrail decisions automatically yield regression tests, which automatically yield counterfactual policy experiments, which automatically yield statistically verified policy updates.

### Experimental Validation

- Reproduce all 11 "Agents of Chaos" cases
- Run full benchmark suite (τ-bench, SWE-bench, GAIA, WebArena, AgentDojo)
- User study (20 engineers, time-to-RCA comparison)
- Counterfactual ACE analysis
- Ablation studies

---

## 📈 Success Metrics

### Year 1 Goals

**Technical:**
- ✅ <50ms p99 inline guardrail latency
- ✅ ≥99.5% replay determinism rate
- ✅ <2ms SDK overhead per span
- ✅ 50k events/s throughput per node

**Adoption:**
- ✅ 5,000 GitHub stars
- ✅ 200 contributors
- ✅ 50 production deployments
- ✅ 10 named enterprise users

**Research:**
- ✅ MLSys paper accepted
- ✅ >100 citations within 24 months
- ✅ Influence OTel GenAI standards

**Community:**
- ✅ Apache 2.0 + DCO governance
- ✅ CNCF sandbox project
- ✅ Active Discord community

---

## 🚀 Go-to-Market Strategy

### Pre-Launch (M4-M6)
- Build in public on GitHub
- Weekly progress threads on X/Bluesky
- Engage Inspect AI Slack, Latent Space Discord

### Soft Launch (M6)
- Show HN with 90-second demo video
- Submit τ-bench pass^k numbers to leaderboard
- Beta program with 10 early adopters

### Hard Launch (M12)
- v1.0 release on Product Hunt
- arXiv paper publication
- Conference talks (KubeCon, QCon, MLSys)
- Case studies from 2 design partners

### Sustainability (M18+)
- Enterprise support program ($5k-$50k/year)
- Professional services
- Cloud provider partnerships
- CNCF incubation

---

## 🎯 Competitive Differentiation

| Feature | Pivot | Inspect AI | Langfuse | LlamaFirewall | LangGraph |
|---------|-------|-----------|----------|---------------|-----------|
| **Evaluation** | ✅ | ✅ | ⚠️ | ❌ | ❌ |
| **Guardrails** | ✅ | ❌ | ❌ | ✅ | ❌ |
| **Replay** | ✅ | ❌ | ❌ | ❌ | ⚠️ |
| **Counterfactual** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Stakeholder Graph** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Framework-Agnostic** | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Production-Grade** | ✅ | ⚠️ | ✅ | ⚠️ | ✅ |

**Unique Value:** The only tool that treats reliability as a unified observable over a single substrate.

---

## 📚 Documentation Structure

```
docs/
├── ULTRA_PLAN.md                    # 18-month roadmap
├── ULTRA_PLAN_PHASE_0.md           # Phase 0 details
├── ULTRA_PLAN_PHASE_1.md           # Phase 1 details
├── ULTRA_PLAN_PHASE_2.md           # Phase 2 details
├── ULTRA_PLAN_PHASE_3.md           # Phase 3 details
├── architecture/
│   └── OVERVIEW.md                  # System architecture
├── research/
│   └── SYNTHESIS.md                 # Research synthesis
├── rfcs/
│   ├── RFC-0001-otel-extensions.md
│   ├── RFC-0002-task-schema.md
│   └── RFC-0003-policy-schema.md
└── benchmarks/
    ├── tau-bench.md
    ├── swe-bench.md
    ├── gaia.md
    ├── webarena.md
    └── aoc-suite.md
```

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Current Focus:**
- RFC reviews and feedback
- Proof of concept validation
- Documentation improvements
- Community building

---

## 📄 License

Apache License 2.0 - see [LICENSE](LICENSE)

**DCO (Developer Certificate of Origin) required for all contributions.**

---

## 🌟 Acknowledgments

Built on research from:
- **Agents of Chaos** team (arXiv:2602.20021)
- **MAST** team (arXiv:2503.13657)
- **ReliabilityBench** team (arXiv:2601.06112v1)
- **OpenTelemetry** GenAI SIG
- **Inspect AI** (UK AISI)
- **Langfuse**, **Phoenix**, **LlamaFirewall** teams

---

## 📬 Contact

- **GitHub:** https://github.com/pivot-ai/pivot
- **Issues:** https://github.com/pivot-ai/pivot/issues
- **Discussions:** https://github.com/pivot-ai/pivot/discussions
- **Email:** hello@pivot.ai (coming soon)
- **Twitter/X:** @pivot_ai (coming soon)

---

## 🗺️ Next Steps

### Immediate (Week 1-2)
1. ✅ Create repository structure
2. ✅ Write comprehensive planning documents
3. [ ] Initialize git repository
4. [ ] Create GitHub repository
5. [ ] Set up CI/CD skeleton

### Short-term (Week 3-4)
1. [ ] Write RFC-0001 (OTel extensions)
2. [ ] Write RFC-0002 (Task schema)
3. [ ] Write RFC-0003 (Policy schema)
4. [ ] Community feedback on RFCs

### Medium-term (Week 5-8)
1. [ ] Build proof of concept
2. [ ] Validate performance targets
3. [ ] Engage early adopters
4. [ ] Finalize Phase 1 plan

---

**Pivot: Making AI agents production-ready, one trace at a time.** 🚀

---

## 📊 Project Statistics

**As of 2026-05-16:**

- **Planning Documents:** 10+ comprehensive documents
- **Total Documentation:** 15,000+ lines
- **Research Papers Analyzed:** 50+
- **GitHub Repos Analyzed:** 40+
- **Architecture Diagrams:** 5+
- **Planned Components:** 8 major components
- **Target Languages:** 4 SDKs (Python, TypeScript, Java, Go)
- **Benchmark Suites:** 6 (τ-bench, SWE-bench, GAIA, WebArena, AgentDojo, AoC)
- **Timeline:** 18 months to production
- **Team Size:** Starting with 1-2 engineers, scaling to 5-10

**Status:** Ready to begin implementation! 🎉
