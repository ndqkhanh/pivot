# Research Synthesis: AI Agent Reliability Harness

**Date:** 2026-05-16  
**Version:** 1.0  
**Authors:** Pivot Research Team

---

## Executive Summary

This document synthesizes research from 50+ papers, 40+ GitHub repositories, and industry best practices to establish the foundation for Pivot - an AI Agent Reliability Harness Platform.

**Key Findings:**
1. **Fragmentation Problem:** Current tools address evaluation, guardrails, or observability in isolation
2. **Missing Primitive:** No system treats deterministic replay as a first-class primitive
3. **Stakeholder Blindness:** Existing guardrails are content-only; they lack principal-awareness
4. **Research Gap:** Agent reliability is under-theorized compared to model capability

**Core Thesis:** Reliability should be measured as a unified observable over a single trace substrate, enabling a closed loop from production failures to verified policy fixes.

---

## 1. Agent Failure Taxonomies

### 1.1 Agents of Chaos (arXiv:2602.20021)

**11 Documented Failure Modes:**

| Case | Type | Root Cause | Impact |
|------|------|------------|--------|
| 1 | Disproportionate response | No blast-radius detection | Deleted mail server |
| 2 | Non-owner compliance | No stakeholder model | 124 emails leaked |
| 3 | Sensitive disclosure | Context-blind PII filter | SSN exposed |
| 4 | Looping | No budget enforcement | 60k tokens, 9 days |
| 5 | DoS | No per-principal quotas | File growth attack |
| 6 | Provider values | Opaque provider behavior | Silent censoring |
| 7 | Agent harm | No social-pressure detection | Guilt/gaslighting |
| 8 | Identity spoofing | Weak identity binding | Owner impersonation |
| 9 | Emergent skill transfer | — | Positive case |
| 10 | Constitution corruption | Untrusted content → policy | Policy poisoning |
| 11 | Libelous broadcast | No audience-size bounds | Reputation damage |

**Key Insight:** Current agents have L4 capability (autonomous execution) but L2 self-awareness (no understanding of their own limitations). This gap is the root cause of most failures.

### 1.2 MAST Taxonomy (arXiv:2503.13657)

**14 Multi-Agent Failure Modes:**

**Specification/Design (5 modes):**
- Ambiguous goals
- Conflicting objectives
- Incomplete task decomposition
- Missing constraints
- Inadequate resource allocation

**Inter-Agent Misalignment (5 modes):**
- Communication failures
- Role confusion
- Resource conflicts
- Inconsistent world models
- Trust violations

**Task Verification (4 modes):**
- Inadequate validation
- Missing checkpoints
- Poor error recovery
- Incomplete rollback

**Validation:** κ=0.88 agreement over 1,642 traces from 7 MAS frameworks

---

## 2. Reliability Frameworks

### 2.1 ReliabilityBench (arXiv:2601.06112v1)

**Reliability Surface:** R(k, ε, λ)

- **k:** Repeated trials (consistency)
  - pass@1 = single-shot success
  - pass^k = success across k trials
  - Measures stochastic flakiness

- **ε:** Perturbation robustness
  - Task paraphrasing
  - UI layout shifts
  - Tool response timing changes
  - Measures brittleness

- **λ:** Fault tolerance
  - Tool timeouts
  - Rate limits
  - Schema drift
  - Partial failures
  - Measures infrastructure resilience

**Key Finding:** Benchmark accuracy compresses away operational flaws. A 90% pass@1 agent may have 60% pass^4 reliability.

### 2.2 Towards a Science of AI Agent Reliability (arXiv:2602.16666v1)

**Four Reliability Dimensions:**

1. **Consistency:** Same input → same output (modulo declared randomness)
2. **Robustness:** Performance under distribution shift
3. **Predictability:** Behavior matches specification
4. **Safety:** No harmful actions

**Thesis:** Accuracy gains do not automatically become reliability gains. Need explicit reliability engineering.

---

## 3. Evaluation Methodologies

### 3.1 Agentic Benchmark Checklist (ABC, arXiv:2507.02825)

**Two Validity Dimensions:**

**Outcome Validity:**
- Does a trivial agent pass? (If yes, task is too easy)
- Does an oracle agent fail? (If yes, oracle is wrong)
- Are success criteria well-defined?
- Can success be automatically verified?

**Task Validity:**
- Is the task underspecified?
- Are there multiple valid solutions?
- Does the task require capabilities it claims to test?
- Is the evaluation metric appropriate?

**Finding:** 7/10 benchmarks violate outcome validity, 7/10 violate task validity

**Implication:** Every eval task needs a validity card documenting these checks.

### 3.2 τ-bench (Sierra Research)

**Key Innovation:** pass^k metric for behavioral reliability

```
pass^k = P(agent succeeds on k independent trials)
```

**Domains:**
- Retail customer service
- Airline booking
- Telecom support

**Simulated Environment:**
- User simulator
- Tool simulator
- Policy simulator

**Finding:** GPT-4 agents show 40% pass@1 but only 15% pass^4 on complex tasks.

### 3.3 Agent GPA (arXiv:2510.08847)

**Factorized Judging:**

Instead of single holistic score, decompose into:
- **Goal:** Did the agent understand the objective?
- **Plan:** Was the plan reasonable?
- **Action:** Were individual actions correct?

**Benefits:**
- 80-95% error coverage on TRAIL/GAIA
- Pinpoints failure location
- Enables targeted fixes

**Integration:** Pivot adopts this as a scorer composition primitive.

---

## 4. Runtime Guardrails

### 4.1 LlamaFirewall (arXiv:2505.03574)

**"Snort/Zeek of LLM Agents"**

**Four Components:**
1. **PromptGuard-2:** Prompt injection detection
2. **AlignmentCheck:** CoT auditor for policy compliance
3. **CodeShield:** Static analysis for generated code
4. **Unified Policy Engine:** Declarative rules

**Latency:**
- Fast rails: <50ms p99
- Slow rails: 200-800ms (async)

**Gap:** Content-only rules; no stakeholder awareness.

### 4.2 SafeHarness (arXiv:2604.13630)

**Lifecycle-Integrated Security:**

**Four Phases:**
1. **INFORM:** Input validation, provenance tracking
2. **VERIFY:** Intent clarification, policy lookup
3. **CONSTRAIN:** Pre-action verification, sandboxing
4. **CORRECT:** Rollback, audit, adaptive degradation

**Key Insight:** Safety is not a post-hoc classifier. It's an execution lifecycle.

**Gap:** No integration with evaluation or replay.

### 4.3 VeriGuard (arXiv:2510.05156)

**Verified Code Generation:**

**Approach:**
1. Offline: Synthesize policy from specifications
2. Online: Monitor actions against policy
3. Verify: Formal verification of generated code

**Domain:** Code generation for safety-critical systems

**Gap:** Formal specs are hard to write; limited to code domain.

---

## 5. Observability & Tracing

### 5.1 OpenTelemetry GenAI v1.37+

**Semantic Conventions:**

**Span Kinds:**
- `gen_ai.client.inference.operation.details`
- `invoke_agent`
- `execute_tool`
- `gen_ai.evaluation.result` (new in v1.37)

**Key Attributes:**
- `gen_ai.operation.name`
- `gen_ai.request.model`
- `gen_ai.usage.input_tokens`
- `gen_ai.usage.output_tokens`
- `gen_ai.conversation.id`

**Adoption:** Langfuse, Phoenix, LangSmith all support OTel export.

### 5.2 Langfuse

**Features:**
- Trace visualization
- Prompt management
- Dataset management
- Evaluation integration
- Cost tracking

**Gap:** No runtime guardrails, no deterministic replay.

### 5.3 Arize Phoenix

**Features:**
- OTel-native ingestion
- Trace search and filtering
- Embedding visualization
- Evaluation experiments

**Gap:** Notebook-flavored; no production guardrails.

---

## 6. Deterministic Replay

### 6.1 LangGraph Time Travel

**Approach:**
- Checkpoint-based persistence
- Replay from checkpoint
- Re-execute nodes after checkpoint

**Limitations:**
- Framework-locked (LangGraph only)
- LLM nodes re-roll (not deterministic)
- No counterfactual operator
- No policy mutation

### 6.2 rr / Pernosco

**Record-and-Replay Debugging:**

**rr (Mozilla):**
- Deterministic recording of native processes
- Byte-identical replay
- Omniscient debugging

**Pernosco:**
- Commercial omniscient debugger
- Time-travel debugging UI
- Causal analysis

**Gap:** Native processes only; not applicable to LLM agents.

### 6.3 Determinism Requirements

**For Byte-Identical Replay:**

1. **Model:** `system_fingerprint` + `seed` honored
2. **Tools:** All I/O recorded and cached
3. **RNG:** All random seeds captured
4. **Time:** Timestamps recorded, not re-sampled
5. **Environment:** Env vars captured

**Providers Supporting Fingerprints:**
- OpenAI: ✅
- Anthropic: ✅
- Google: ❌
- Cohere: ❌

---

## 7. Causal Inference for Agents

### 7.1 Pearl's do-Calculus

**Counterfactual Query:**

```
P(Y=y | do(X=x), Z=z)
```

**For Agents:**
- Y = outcome (score, success)
- X = intervention (policy, model, prompt)
- Z = observed context (task, environment)

**Identifiability:**
- **Agent-internal variables** (policy, prompt, model): Identifiable (we control sampling)
- **Environmental variables** (tool responses, user input): Requires importance weighting

### 7.2 Buesing et al. (2019)

**Counterfactual RL:**

**Approach:**
- Record trajectories with behavior policy π_b
- Estimate counterfactual under target policy π_t
- Use importance sampling for unobserved actions

**Application to Agents:**
- Behavior policy = original agent policy
- Target policy = proposed fix
- Estimate ACE (Average Counterfactual Effect)

---

## 8. Competitive Landscape

### 8.1 Tool Comparison Matrix

| Tool | Eval | Guardrails | Replay | Substrate | License |
|------|------|------------|--------|-----------|---------|
| **Inspect AI** | ✅ | ❌ | ❌ | Task-centric | MIT |
| **Langfuse** | ⚠️ | ❌ | ❌ | Trace-centric | MIT |
| **Phoenix** | ⚠️ | ❌ | ❌ | Trace-centric | Elastic 2.0 |
| **LangSmith** | ✅ | ❌ | ⚠️ | Trace-centric | Closed |
| **NeMo Guardrails** | ❌ | ✅ | ❌ | Policy-centric | Apache 2.0 |
| **LlamaFirewall** | ❌ | ✅ | ❌ | Policy-centric | MIT |
| **LangGraph** | ❌ | ❌ | ⚠️ | Framework-locked | MIT |
| **Pivot** | ✅ | ✅ | ✅ | Unified substrate | Apache 2.0 |

Legend: ✅ Full support, ⚠️ Partial support, ❌ No support

### 8.2 Differentiation Strategy

**Pivot's Unique Value:**

1. **Unified Substrate:** Three pillars as queries over one log
2. **Deterministic Replay:** First-class primitive, not bolt-on
3. **Stakeholder Graph:** Principal-aware policies
4. **Counterfactual Operator:** Causal analysis of interventions
5. **Framework-Agnostic:** Works with any agent framework
6. **Production-Grade:** Built for scale, not research

---

## 9. Research Gaps & Opportunities

### 9.1 Publishable Contributions

| Gap | Opportunity | Venue |
|-----|-------------|-------|
| Unified reliability substrate | Three pillars as queries on one log | MLSys |
| Counterfactual replay | Pearl's do-operator for agent traces | MLSys / NeurIPS |
| Stakeholder-aware policies | Principal-parameterized guardrails | COLM / FAccT |
| Trace-grounded evaluation | Production traces as regression tests | ICSE / FSE |
| Judge reliability | Calibrated LLM-as-judge with uncertainty | EMNLP |

### 9.2 Open Research Questions

1. **Replay Determinism:** What is the theoretical limit for LLM agent replay determinism?
2. **Counterfactual Identifiability:** When can we identify causal effects from agent traces?
3. **Stakeholder Inference:** Can we automatically infer stakeholder graphs from traces?
4. **Policy Synthesis:** Can we synthesize guardrail policies from failure traces?
5. **Reliability Metrics:** What is the right reliability metric for production agents?

---

## 10. Conclusion

**Key Takeaways:**

1. **Problem is Real:** 11 documented failure modes (AoC) + 14 multi-agent modes (MAST)
2. **Current Tools are Fragmented:** No unified substrate
3. **Research Foundation is Strong:** 50+ papers provide theoretical grounding
4. **Market Opportunity is Clear:** Every production agent needs reliability engineering
5. **Technical Feasibility is Proven:** All components have prior art

**Pivot's Contribution:**

> The first production-grade platform that unifies evaluation, guardrails, and deterministic replay over a single OpenTelemetry-native substrate, enabling a closed reliability loop from production failures to verified policy fixes.

**Next Steps:**

1. Finalize RFCs (OTel extensions, task schema, policy schema)
2. Build proof of concept (Python SDK + Gateway + ClickHouse)
3. Validate with early adopters
4. Iterate toward MVP (Phase 1)

---

## References

See [REFERENCES.md](REFERENCES.md) for complete bibliography (50+ papers, 40+ repos).
