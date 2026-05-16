"""
Online Evaluation System

Mirrors production traffic to eval engine for continuous monitoring
Includes drift detection and alerting
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Callable
import asyncio
from datetime import datetime


@dataclass
class OnlineEvalConfig:
    """Configuration for online evaluation"""
    enabled: bool = True
    sample_rate: float = 0.1  # 10% of production runs
    scorers: List[str] = None
    alert_threshold: float = 0.7
    alert_webhook: Optional[str] = None


@dataclass
class DriftAlert:
    """Alert for detected drift"""
    timestamp: datetime
    metric: str
    current_value: float
    baseline_value: float
    drift_magnitude: float
    severity: str  # "warning" or "critical"


class OnlineEvaluator:
    """
    Continuous evaluation of production agent runs

    Features:
    - Traffic sampling
    - Async scoring
    - Drift detection (CUSUM)
    - Alerting integration
    """

    def __init__(self, config: OnlineEvalConfig, scorers: Dict[str, Callable]):
        self.config = config
        self.scorers = scorers
        self.baseline_scores: Dict[str, List[float]] = {}
        self.drift_detector = CUSUMDriftDetector()

    async def evaluate_run(self, run_id: str, run_data: Dict[str, Any]) -> None:
        """
        Evaluate a production run asynchronously

        Args:
            run_id: Run identifier
            run_data: Run metadata and results
        """
        if not self.config.enabled:
            return

        # Sample based on rate
        if not self._should_sample():
            return

        # Score asynchronously
        scores = await self._score_async(run_id, run_data)

        # Check for drift
        for metric, score in scores.items():
            drift = self.drift_detector.detect(metric, score)

            if drift:
                await self._send_alert(drift)

        # Store scores
        for metric, score in scores.items():
            if metric not in self.baseline_scores:
                self.baseline_scores[metric] = []
            self.baseline_scores[metric].append(score)

    async def _score_async(
        self,
        run_id: str,
        run_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """Score run with all configured scorers"""
        tasks = []

        for scorer_name in self.config.scorers or []:
            if scorer_name in self.scorers:
                scorer = self.scorers[scorer_name]
                tasks.append(scorer(run_data))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        scores = {}
        for scorer_name, result in zip(self.config.scorers or [], results):
            if not isinstance(result, Exception):
                scores[scorer_name] = result

        return scores

    def _should_sample(self) -> bool:
        """Determine if this run should be sampled"""
        import random
        return random.random() < self.config.sample_rate

    async def _send_alert(self, drift: DriftAlert) -> None:
        """Send alert for detected drift"""
        if self.config.alert_webhook:
            # Send to webhook (Slack, PagerDuty, etc.)
            print(f"ALERT: Drift detected in {drift.metric}")
            print(f"  Current: {drift.current_value:.3f}")
            print(f"  Baseline: {drift.baseline_value:.3f}")
            print(f"  Magnitude: {drift.drift_magnitude:.3f}")


class CUSUMDriftDetector:
    """
    CUSUM (Cumulative Sum) drift detection

    Detects when metric drifts from baseline
    """

    def __init__(self, threshold: float = 5.0):
        self.threshold = threshold
        self.cumsum: Dict[str, float] = {}
        self.baseline: Dict[str, float] = {}

    def detect(self, metric: str, value: float) -> Optional[DriftAlert]:
        """
        Detect drift in metric

        Returns DriftAlert if drift detected, None otherwise
        """
        # Initialize baseline
        if metric not in self.baseline:
            self.baseline[metric] = value
            self.cumsum[metric] = 0.0
            return None

        # Calculate deviation
        deviation = value - self.baseline[metric]

        # Update CUSUM
        self.cumsum[metric] = max(0, self.cumsum[metric] + deviation)

        # Check threshold
        if self.cumsum[metric] > self.threshold:
            drift_magnitude = abs(value - self.baseline[metric])

            return DriftAlert(
                timestamp=datetime.utcnow(),
                metric=metric,
                current_value=value,
                baseline_value=self.baseline[metric],
                drift_magnitude=drift_magnitude,
                severity="critical" if drift_magnitude > 0.2 else "warning"
            )

        return None
