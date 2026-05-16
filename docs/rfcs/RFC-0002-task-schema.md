# RFC-0002: Task Schema for Agent Evaluation

**Status:** Draft  
**Author:** Pivot Team  
**Created:** 2026-05-16  
**Updated:** 2026-05-16

---

## Summary

This RFC defines a YAML-first evaluation task format for agent reliability testing. The schema enables declarative task definition, reproducible evaluation, and statistical rigor while maintaining compatibility with Inspect AI and other evaluation frameworks.

---

## Motivation

Current agent evaluation frameworks have limitations:

1. **Code-first definitions** - Tasks defined in Python/TypeScript, not portable
2. **Inconsistent schemas** - Each framework has different task formats
3. **Missing reliability metrics** - No built-in support for pass^k, bootstrap CI
4. **No policy integration** - Can't test agents under different guardrail policies
5. **Limited reproducibility** - Hard to share and reproduce evaluations

We need a **declarative, portable, statistically rigorous** task format.

---

## Proposal

### Schema Version

```yaml
schema_version: "1.0"
```

All tasks must declare schema version for forward compatibility.

### Complete Task Schema

```yaml
# Task metadata
name: string                    # Unique task identifier
version: string                 # Task version (semver)
description: string             # Human-readable description
tags: [string]                  # Searchable tags
author: string                  # Task author
created: string                 # ISO 8601 timestamp
updated: string                 # ISO 8601 timestamp

# Dataset configuration
dataset:
  type: enum                    # local | remote | synthetic | huggingface
  source: string                # Path, URL, or HF dataset ID
  format: enum                  # jsonl | csv | parquet | json
  split: string                 # train | test | validation
  subset: string                # Optional subset name
  sample_size: int              # Optional: limit dataset size
  shuffle: boolean              # Shuffle dataset
  seed: int                     # Random seed for reproducibility

# Solver configuration (how to run the agent)
solver:
  type: enum                    # react | plan_execute | custom | chain_of_thought
  max_steps: int                # Maximum reasoning steps
  timeout_seconds: int          # Per-sample timeout
  model: string                 # Model identifier (e.g., "gpt-4")
  temperature: float            # Temperature parameter
  max_tokens: int               # Max output tokens
  system_prompt: string         # Optional system prompt override
  tools: [string]               # Available tools
  custom_solver_path: string    # Path to custom solver (if type=custom)

# Scoring configuration
scorers:
  - type: enum                  # exact | regex | json_schema | rubric_judge | ...
    name: string                # Scorer identifier
    weight: float               # Weight in final score (default: 1.0)
    config: object              # Scorer-specific configuration

# Metrics and statistical analysis
metrics:
  - name: string                # pass@1 | pass@4 | pass@8 | accuracy | f1 | ...
    aggregation: enum           # mean | median | p95 | bootstrap_ci
    bootstrap_samples: int      # For bootstrap_ci (default: 10000)
    confidence_level: float     # For CI (default: 0.95)

# Execution configuration
execution:
  epochs: int                   # Number of repeated runs (for pass^k)
  concurrency: int              # Parallel execution
  retry_on_error: boolean       # Retry failed samples
  max_retries: int              # Maximum retries per sample

# Sandbox configuration
sandbox:
  type: enum                    # gvisor | firecracker | docker | none
  image: string                 # Container image
  resources:
    vcpu: int
    memory_mb: int
    disk_mb: int
    timeout_seconds: int
  network:
    egress_allowed: boolean
    allowed_domains: [string]

# Policy configuration (guardrails to test under)
policy:
  name: string                  # Policy pack name
  version: string               # Policy version
  enabled: boolean              # Enable policy enforcement
  fail_on_violation: boolean    # Fail task if policy violated

# Validation (ABC checklist compliance)
validation:
  outcome_validity:
    trivial_agent_should_fail: boolean
    oracle_agent_should_pass: boolean
  task_validity:
    well_specified: boolean
    single_correct_answer: boolean
    capabilities_tested: [string]

# Metadata
metadata:
  difficulty: enum              # easy | medium | hard
  domain: string                # coding | web | reasoning | ...
  estimated_cost_usd: float     # Estimated cost per run
  estimated_time_seconds: int   # Estimated time per run
```

---

## Scorer Types

### Built-in Scorers

#### 1. Exact Match
```yaml
scorers:
  - type: exact
    name: exact_match
    config:
      case_sensitive: false
      normalize_whitespace: true
```

#### 2. Regex Match
```yaml
scorers:
  - type: regex
    name: regex_match
    config:
      pattern: "^[0-9]{3}-[0-9]{2}-[0-9]{4}$"
      flags: [IGNORECASE, MULTILINE]
```

#### 3. JSON Schema Validation
```yaml
scorers:
  - type: json_schema
    name: json_validator
    config:
      schema:
        type: object
        properties:
          name: {type: string}
          age: {type: integer}
        required: [name, age]
```

#### 4. Programmatic Scorer
```yaml
scorers:
  - type: programmatic
    name: custom_scorer
    config:
      script_path: "./scorers/custom.py"
      function_name: "score"
      sandbox: true
```

#### 5. LLM-as-Judge (Rubric)
```yaml
scorers:
  - type: rubric_judge
    name: quality_judge
    config:
      model: claude-sonnet-4
      rubric: |
        Score the response on:
        1. Correctness (0-5)
        2. Completeness (0-5)
        3. Safety (0-5)
      bias_mitigation:
        position_swap: true
        ensemble_size: 3
        verbosity_control: true
```

#### 6. SWE-bench Verifier
```yaml
scorers:
  - type: swe_bench_verifier
    name: swe_verifier
    config:
      test_command: "pytest tests/"
      timeout_seconds: 300
```

#### 7. Pass^k Scorer
```yaml
scorers:
  - type: pass_k
    name: pass_at_4
    config:
      k: 4
      base_scorer: exact_match
```

---

## Example Tasks

### Example 1: τ-bench Retail Task

```yaml
schema_version: "1.0"
name: "tau_bench_retail_001"
version: "1.0.0"
description: "Customer service task: process return request"
tags: [tau-bench, retail, customer-service]

dataset:
  type: local
  source: "./datasets/tau_bench_retail.jsonl"
  format: jsonl
  shuffle: true
  seed: 42

solver:
  type: react
  max_steps: 20
  timeout_seconds: 120
  model: "gpt-4"
  temperature: 0.7
  tools: [check_order, process_return, send_email]

scorers:
  - type: exact
    name: outcome_match
    weight: 0.5
  - type: rubric_judge
    name: process_quality
    weight: 0.5
    config:
      model: claude-sonnet-4
      rubric: |
        Did the agent:
        1. Verify order details correctly?
        2. Follow return policy?
        3. Communicate clearly with customer?

metrics:
  - name: pass@1
    aggregation: mean
  - name: pass@4
    aggregation: mean
  - name: accuracy
    aggregation: bootstrap_ci
    bootstrap_samples: 10000

execution:
  epochs: 4
  concurrency: 2
  retry_on_error: false

sandbox:
  type: gvisor
  resources:
    vcpu: 1
    memory_mb: 512
    timeout_seconds: 180

policy:
  name: customer_service_safe
  version: "1.0"
  enabled: true
  fail_on_violation: true

validation:
  outcome_validity:
    trivial_agent_should_fail: true
    oracle_agent_should_pass: true
  task_validity:
    well_specified: true
    single_correct_answer: false
    capabilities_tested: [reasoning, tool_use, policy_compliance]

metadata:
  difficulty: medium
  domain: customer-service
  estimated_cost_usd: 0.05
  estimated_time_seconds: 30
```

### Example 2: SWE-bench Task

```yaml
schema_version: "1.0"
name: "swe_bench_django_001"
version: "1.0.0"
description: "Fix Django ORM bug in queryset filtering"
tags: [swe-bench, coding, django]

dataset:
  type: local
  source: "./datasets/swe_bench_verified.jsonl"
  format: jsonl
  sample_size: 1

solver:
  type: plan_execute
  max_steps: 50
  timeout_seconds: 600
  model: "claude-opus-4"
  temperature: 0.0
  tools: [read_file, write_file, run_tests, search_code]

scorers:
  - type: swe_bench_verifier
    name: test_pass
    config:
      test_command: "pytest tests/test_queryset.py"
      timeout_seconds: 300

metrics:
  - name: pass@1
    aggregation: mean
  - name: pass@8
    aggregation: mean

execution:
  epochs: 8
  concurrency: 4
  retry_on_error: false

sandbox:
  type: docker
  image: "python:3.11-slim"
  resources:
    vcpu: 2
    memory_mb: 4096
    disk_mb: 10240
    timeout_seconds: 900
  network:
    egress_allowed: false

policy:
  name: coding_agent_safe
  version: "1.0"
  enabled: true

metadata:
  difficulty: hard
  domain: coding
  estimated_cost_usd: 0.50
  estimated_time_seconds: 300
```

---

## Compatibility with Inspect AI

Tasks can be imported from Inspect AI format:

```python
from pivot.eval import Task

# Load Pivot task
task = Task.from_yaml("task.yaml")

# Convert to Inspect AI format
inspect_task = task.to_inspect_ai()

# Import from Inspect AI
pivot_task = Task.from_inspect_ai(inspect_task)
```

---

## JSON Schema

Full JSON Schema available at: `spec/schemas/task-schema-v1.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["schema_version", "name", "dataset", "solver", "scorers"],
  "properties": {
    "schema_version": {"type": "string", "const": "1.0"},
    "name": {"type": "string", "pattern": "^[a-z0-9_-]+$"},
    ...
  }
}
```

---

## Implementation

### Task Loader

```python
from pivot.eval import Task

# Load from YAML
task = Task.from_yaml("task.yaml")

# Validate
task.validate()

# Run
results = task.run()

# Get metrics
print(results.metrics["pass@1"])  # 0.75
print(results.metrics["pass@4"])  # 0.60
print(results.confidence_intervals["accuracy"])  # (0.68, 0.82)
```

### Task Runner

```python
class TaskRunner:
    def run(self, task: Task) -> TaskResult:
        # Load dataset
        dataset = self.load_dataset(task.dataset)
        
        # Run epochs
        results = []
        for epoch in range(task.execution.epochs):
            for sample in dataset:
                result = self.run_sample(sample, task.solver)
                score = self.score(result, task.scorers)
                results.append(score)
        
        # Compute metrics
        metrics = self.compute_metrics(results, task.metrics)
        
        return TaskResult(metrics=metrics, results=results)
```

---

## Alternatives Considered

### 1. Python-first (like Inspect AI)

**Rejected:** Not portable across languages, harder to share.

### 2. JSON instead of YAML

**Rejected:** YAML is more human-readable for config files.

### 3. Separate files for dataset/solver/scorers

**Rejected:** Single file is easier to share and version.

---

## Unresolved Questions

1. **Should we support task composition?**
   - Proposal: Add `extends: parent_task.yaml` for inheritance
   
2. **Should we support dynamic datasets?**
   - Proposal: Add `dataset.generator` for synthetic data

3. **How to handle large datasets?**
   - Proposal: Support streaming from S3/HuggingFace

---

## Success Criteria

1. ✅ Can define any evaluation task in YAML
2. ✅ Compatible with Inspect AI tasks
3. ✅ Supports all scorer types
4. ✅ Enables pass^k and bootstrap CI
5. ✅ Validates against JSON Schema
6. ✅ Portable across languages

---

## References

- [Inspect AI Task Format](https://inspect.ai-safety-institute.org.uk/tasks.html)
- [τ-bench Paper](https://arxiv.org/abs/2406.12045)
- [SWE-bench Paper](https://arxiv.org/abs/2310.06770)
- [ABC Checklist](https://arxiv.org/abs/2507.02825)

---

## Changelog

- **2026-05-16:** Initial draft
