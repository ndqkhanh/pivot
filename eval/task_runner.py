"""
Pivot Evaluation Engine

Task runner with statistical analysis for agent evaluation.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Callable
import yaml
import json
from pathlib import Path


@dataclass
class TaskConfig:
    """Task configuration loaded from YAML."""

    name: str
    version: str
    description: str
    dataset: Dict[str, Any]
    solver: Dict[str, Any]
    scorers: List[Dict[str, Any]]
    metrics: List[Dict[str, Any]]
    execution: Dict[str, Any]


@dataclass
class SampleResult:
    """Result for a single sample."""

    sample_id: str
    input: Any
    output: Any
    score: float
    success: bool
    metadata: Dict[str, Any]


@dataclass
class TaskResult:
    """Aggregated results for a task."""

    task_name: str
    total_samples: int
    successful_samples: int
    metrics: Dict[str, float]
    sample_results: List[SampleResult]


class TaskRunner:
    """Runs evaluation tasks and computes metrics."""

    def __init__(self, task_path: str):
        """
        Initialize task runner.

        Args:
            task_path: Path to task YAML file
        """
        self.task_path = Path(task_path)
        self.config = self._load_config()

    def _load_config(self) -> TaskConfig:
        """Load task configuration from YAML."""
        with open(self.task_path) as f:
            data = yaml.safe_load(f)

        return TaskConfig(
            name=data["name"],
            version=data["version"],
            description=data["description"],
            dataset=data["dataset"],
            solver=data["solver"],
            scorers=data["scorers"],
            metrics=data["metrics"],
            execution=data["execution"]
        )

    def run(self, solver_fn: Callable) -> TaskResult:
        """
        Run the evaluation task.

        Args:
            solver_fn: Function that takes input and returns output

        Returns:
            TaskResult with aggregated metrics
        """
        # Load dataset
        dataset = self._load_dataset()

        # Run epochs
        all_results = []
        epochs = self.config.execution.get("epochs", 1)

        for epoch in range(epochs):
            for sample in dataset:
                # Run solver
                output = solver_fn(sample["input"])

                # Score output
                score = self._score_output(output, sample.get("expected"))

                result = SampleResult(
                    sample_id=sample["id"],
                    input=sample["input"],
                    output=output,
                    score=score,
                    success=score >= 0.5,  # Threshold
                    metadata={"epoch": epoch}
                )
                all_results.append(result)

        # Compute metrics
        metrics = self._compute_metrics(all_results)

        return TaskResult(
            task_name=self.config.name,
            total_samples=len(all_results),
            successful_samples=sum(1 for r in all_results if r.success),
            metrics=metrics,
            sample_results=all_results
        )

    def _load_dataset(self) -> List[Dict[str, Any]]:
        """Load dataset from source."""
        dataset_config = self.config.dataset
        source = dataset_config["source"]
        format_type = dataset_config["format"]

        if format_type == "jsonl":
            with open(source) as f:
                return [json.loads(line) for line in f]
        else:
            raise ValueError(f"Unsupported format: {format_type}")

    def _score_output(self, output: Any, expected: Any) -> float:
        """Score output using configured scorers."""
        scores = []

        for scorer_config in self.config.scorers:
            scorer_type = scorer_config["type"]
            weight = scorer_config.get("weight", 1.0)

            if scorer_type == "exact":
                score = 1.0 if output == expected else 0.0
            elif scorer_type == "regex":
                import re
                pattern = scorer_config["config"]["pattern"]
                score = 1.0 if re.match(pattern, str(output)) else 0.0
            else:
                score = 0.0

            scores.append(score * weight)

        return sum(scores) / len(scores) if scores else 0.0

    def _compute_metrics(self, results: List[SampleResult]) -> Dict[str, float]:
        """Compute configured metrics."""
        metrics = {}

        for metric_config in self.config.metrics:
            metric_name = metric_config["name"]

            if metric_name == "pass@1":
                # Single-shot success rate
                metrics["pass@1"] = sum(r.success for r in results) / len(results)

            elif metric_name.startswith("pass@"):
                # pass@k metric
                k = int(metric_name.split("@")[1])
                metrics[metric_name] = self._compute_pass_k(results, k)

            elif metric_name == "accuracy":
                metrics["accuracy"] = sum(r.score for r in results) / len(results)

        return metrics

    def _compute_pass_k(self, results: List[SampleResult], k: int) -> float:
        """Compute pass@k metric."""
        # Group by sample_id
        by_sample = {}
        for r in results:
            if r.sample_id not in by_sample:
                by_sample[r.sample_id] = []
            by_sample[r.sample_id].append(r)

        # Check if any of k attempts succeeded
        pass_count = 0
        for sample_results in by_sample.values():
            if any(r.success for r in sample_results[:k]):
                pass_count += 1

        return pass_count / len(by_sample)


def run_task(task_path: str, solver_fn: Callable) -> TaskResult:
    """
    Convenience function to run a task.

    Args:
        task_path: Path to task YAML
        solver_fn: Solver function

    Returns:
        TaskResult

    Example:
        >>> def my_solver(input_text):
        ...     return "answer"
        >>> result = run_task("task.yaml", my_solver)
        >>> print(result.metrics["pass@1"])
    """
    runner = TaskRunner(task_path)
    return runner.run(solver_fn)
