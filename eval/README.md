# Pivot Evaluation Engine

Statistical evaluation framework for agent reliability testing.

## Features

- **YAML-first tasks**: Declarative task definitions
- **Built-in scorers**: Exact, regex, JSON schema, LLM-as-judge
- **Statistical rigor**: pass@k, bootstrap CI
- **Framework adapters**: τ-bench, SWE-bench, GAIA

## Quick Start

```python
from pivot.eval import run_task

# Define solver
def my_solver(input_text):
    # Your agent logic here
    return "answer"

# Run task
result = run_task("task.yaml", my_solver)

# Check metrics
print(f"pass@1: {result.metrics['pass@1']}")
print(f"pass@4: {result.metrics['pass@4']}")
```

## Task Format

```yaml
name: my_task
version: "1.0.0"
description: "Test task"

dataset:
  type: local
  source: "./data.jsonl"
  format: jsonl

solver:
  type: react
  max_steps: 20
  model: "gpt-4"

scorers:
  - type: exact
    weight: 1.0

metrics:
  - name: pass@1
  - name: pass@4

execution:
  epochs: 4
  concurrency: 2
```

## Built-in Scorers

- **exact**: Exact string match
- **regex**: Pattern matching
- **json_schema**: JSON validation
- **rubric_judge**: LLM-as-judge (coming soon)

## Statistical Analysis

- **pass@k**: Success rate across k trials
- **Bootstrap CI**: Confidence intervals
- **Reliability surface**: R(k,ε,λ)

## License

Apache 2.0
