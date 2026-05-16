# Pivot - Documentation Index

**Welcome to Pivot!** This index helps you navigate the comprehensive planning documentation.

---

## 🚀 Quick Start

**New to Pivot?** Start here:
1. [README.md](README.md) - Project overview and vision
2. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Comprehensive project summary
3. [docs/ULTRA_PLAN.md](docs/ULTRA_PLAN.md) - 18-month roadmap

**Want to contribute?**
1. [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
2. [LICENSE](LICENSE) - Apache 2.0 license

---

## 📋 Planning Documents

### Strategic Planning

| Document | Description | Status |
|----------|-------------|--------|
| [ULTRA_PLAN.md](docs/ULTRA_PLAN.md) | Master 18-month roadmap | ✅ Complete |
| [ULTRA_PLAN_PHASE_0.md](docs/ULTRA_PLAN_PHASE_0.md) | Foundation phase (M1-2) | ✅ Complete |
| [ULTRA_PLAN_PHASE_1.md](docs/ULTRA_PLAN_PHASE_1.md) | MVP phase (M3-6) | ✅ Complete |
| [ULTRA_PLAN_PHASE_2.md](docs/ULTRA_PLAN_PHASE_2.md) | V1.0 phase (M7-12) | ✅ Complete |
| [ULTRA_PLAN_PHASE_3.md](docs/ULTRA_PLAN_PHASE_3.md) | Production phase (M13-18) | ✅ Complete |

### Technical Documentation

| Document | Description | Status |
|----------|-------------|--------|
| [architecture/OVERVIEW.md](docs/architecture/OVERVIEW.md) | System architecture deep-dive | ✅ Complete |
| [research/SYNTHESIS.md](docs/research/SYNTHESIS.md) | Research literature synthesis | ✅ Complete |

### RFCs (Coming Soon)

| RFC | Title | Status |
|-----|-------|--------|
| RFC-0001 | OpenTelemetry Extensions | 📋 Planned |
| RFC-0002 | Task Schema | 📋 Planned |
| RFC-0003 | Policy Schema | 📋 Planned |

---

## 🎯 By Role

### For Engineers

**Getting Started:**
- [architecture/OVERVIEW.md](docs/architecture/OVERVIEW.md) - System design
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development setup

**Implementation:**
- [ULTRA_PLAN_PHASE_1.md](docs/ULTRA_PLAN_PHASE_1.md) - MVP features
- RFCs (coming soon) - Technical specifications

### For Researchers

**Research Foundation:**
- [research/SYNTHESIS.md](docs/research/SYNTHESIS.md) - 50+ papers analyzed
- [ULTRA_PLAN_PHASE_3.md](docs/ULTRA_PLAN_PHASE_3.md) - Academic paper plan

**Novel Contributions:**
1. Unified substrate (three pillars as queries)
2. Counterfactual replay (Pearl's do-operator)
3. Stakeholder graph (principal-aware policies)

### For Product Managers

**Strategy:**
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Executive summary
- [ULTRA_PLAN.md](docs/ULTRA_PLAN.md) - Roadmap and milestones

**Go-to-Market:**
- [ULTRA_PLAN_PHASE_2.md](docs/ULTRA_PLAN_PHASE_2.md) - Launch strategy
- [ULTRA_PLAN_PHASE_3.md](docs/ULTRA_PLAN_PHASE_3.md) - Enterprise features

### For Community Members

**Understanding Pivot:**
- [README.md](README.md) - Vision and features
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Comprehensive overview

**Contributing:**
- [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute
- GitHub Issues - Bug reports and feature requests

---

## 📊 Project Phases

### Phase 0: Foundation (M1-2) - 🔄 Current

**Goal:** Establish project foundation and specifications

**Key Deliverables:**
- ✅ Repository structure
- ✅ Planning documents
- ✅ Research synthesis
- ✅ Architecture design
- 📋 RFCs (in progress)
- 📋 Proof of concept

**Timeline:** Weeks 1-8

### Phase 1: MVP (M3-6)

**Goal:** Build functional MVP with core features

**Key Deliverables:**
- Python SDK
- Gateway v0
- Eval engine v0
- Replay engine v0
- 8 core guardrails
- Console UI
- v0.1 release

**Timeline:** Weeks 9-24

### Phase 2: V1.0 (M7-12)

**Goal:** Production-ready platform

**Key Deliverables:**
- Polyglot SDKs (TS, Java, Go)
- Counterfactual replay
- LLM-as-judge
- Failure clustering
- CI/CD integration
- v1.0 release

**Timeline:** Weeks 25-48

### Phase 3: Production Hardening (M13-18)

**Goal:** Industry standard with academic validation

**Key Deliverables:**
- MLSys paper
- CNCF sandbox
- Enterprise features
- Global deployment
- Community governance

**Timeline:** Weeks 49-72

---

## 🔍 By Topic

### Evaluation
- [architecture/OVERVIEW.md#eval-engine](docs/architecture/OVERVIEW.md) - Eval architecture
- [ULTRA_PLAN_PHASE_1.md#eval-engine](docs/ULTRA_PLAN_PHASE_1.md) - Implementation plan
- [research/SYNTHESIS.md#evaluation](docs/research/SYNTHESIS.md) - Research foundation

### Guardrails
- [architecture/OVERVIEW.md#gateway](docs/architecture/OVERVIEW.md) - Gateway architecture
- [ULTRA_PLAN_PHASE_1.md#guardrails](docs/ULTRA_PLAN_PHASE_1.md) - Implementation plan
- [research/SYNTHESIS.md#guardrails](docs/research/SYNTHESIS.md) - Research foundation

### Replay
- [architecture/OVERVIEW.md#replay-engine](docs/architecture/OVERVIEW.md) - Replay architecture
- [ULTRA_PLAN_PHASE_1.md#replay-engine](docs/ULTRA_PLAN_PHASE_1.md) - Implementation plan
- [research/SYNTHESIS.md#replay](docs/research/SYNTHESIS.md) - Research foundation

### Benchmarks
- [research/SYNTHESIS.md#benchmarks](docs/research/SYNTHESIS.md) - Benchmark analysis
- [ULTRA_PLAN_PHASE_1.md#benchmarks](docs/ULTRA_PLAN_PHASE_1.md) - Benchmark adapters

---

## 📈 Success Metrics

### Technical Targets
- <50ms p99 inline guardrail latency
- ≥99.5% replay determinism rate
- <2ms SDK overhead per span
- 50k events/s throughput per node

### Adoption Targets (Year 1)
- 5,000 GitHub stars
- 200 contributors
- 50 production deployments
- 10 named enterprise users

### Research Targets
- MLSys paper accepted
- >100 citations within 24 months
- Influence OTel GenAI standards

---

## 🗺️ Roadmap Visualization

```
Month 1-2  [████████░░░░░░░░░░░░░░░░░░░░░░░░] Phase 0: Foundation
Month 3-6  [░░░░░░░░████████████░░░░░░░░░░░░] Phase 1: MVP
Month 7-12 [░░░░░░░░░░░░░░░░░░░░████████████] Phase 2: V1.0
Month 13-18[░░░░░░░░░░░░░░░░░░░░░░░░░░░░████] Phase 3: Production

Current: Phase 0, Week 1 ⭐
```

---

## 🤝 Community

### Communication Channels
- **GitHub Issues:** Bug reports, feature requests
- **GitHub Discussions:** Questions, ideas
- **Discord:** Real-time chat (coming soon)
- **Twitter/X:** @pivot_ai (coming soon)

### Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup
- Code style guidelines
- Pull request process
- RFC process

---

## 📚 Additional Resources

### External Links
- **OpenTelemetry GenAI:** https://opentelemetry.io/docs/specs/semconv/gen-ai/
- **Agents of Chaos Paper:** https://arxiv.org/abs/2602.20021
- **MAST Paper:** https://arxiv.org/abs/2503.13657
- **ReliabilityBench Paper:** https://arxiv.org/abs/2601.06112v1

### Related Projects
- **Inspect AI:** https://github.com/UKGovernmentBEIS/inspect_ai
- **Langfuse:** https://github.com/langfuse/langfuse
- **Phoenix:** https://github.com/Arize-ai/phoenix
- **LlamaFirewall:** https://github.com/meta-llama/llama-firewall

---

## 📝 Document Status Legend

- ✅ **Complete** - Document is finished and reviewed
- 🔄 **In Progress** - Document is being written
- 📋 **Planned** - Document is planned but not started
- ⚠️ **Needs Update** - Document needs revision

---

## 🎯 Next Steps

### This Week
1. ✅ Create repository structure
2. ✅ Write planning documents
3. [ ] Initialize git repository
4. [ ] Create GitHub repository
5. [ ] Set up CI/CD skeleton

### Next Week
1. [ ] Write RFC-0001 (OTel extensions)
2. [ ] Write RFC-0002 (Task schema)
3. [ ] Write RFC-0003 (Policy schema)
4. [ ] Community feedback on RFCs

### This Month
1. [ ] Build proof of concept
2. [ ] Validate performance targets
3. [ ] Engage early adopters
4. [ ] Finalize Phase 1 plan

---

## 📬 Questions?

- Open a [GitHub Discussion](https://github.com/pivot-ai/pivot/discussions) (coming soon)
- Email: hello@pivot.ai (coming soon)

---

**Last Updated:** 2026-05-16  
**Version:** 1.0  
**Status:** Phase 0 - Foundation

---

**Pivot: Making AI agents production-ready, one trace at a time.** 🚀
