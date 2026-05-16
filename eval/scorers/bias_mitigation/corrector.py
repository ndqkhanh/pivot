"""
Bias mitigation techniques for LLM-as-judge

Implements strategies to reduce systematic biases:
- Position bias correction
- Verbosity normalization
- Self-preference detection
- Calibration against human labels
"""

from typing import List, Tuple
import numpy as np


class BiasCorrector:
    """Corrects for systematic biases in LLM judging"""

    def __init__(self):
        self.calibration_data = []

    def correct_position_bias(
        self,
        score_first: float,
        score_second: float
    ) -> float:
        """
        Correct for position bias using position swap

        Average scores from both positions to cancel bias
        """
        return (score_first + score_second) / 2.0

    def normalize_verbosity(
        self,
        response: str,
        score: float
    ) -> float:
        """
        Normalize score for response length

        Longer responses tend to get higher scores
        """
        length = len(response.split())

        # Apply length penalty for very long responses
        if length > 500:
            penalty = min(0.1, (length - 500) / 5000)
            return max(0.0, score - penalty)

        return score

    def detect_self_preference(
        self,
        judge_model: str,
        response_model: str,
        score: float
    ) -> Tuple[bool, float]:
        """
        Detect if judge shows self-preference bias

        Returns (is_biased, corrected_score)
        """
        # Check if same model family
        is_same_family = self._same_model_family(judge_model, response_model)

        if is_same_family and score > 0.8:
            # Potential self-preference, apply correction
            corrected = score * 0.95
            return True, corrected

        return False, score

    def calibrate_with_human_labels(
        self,
        llm_scores: List[float],
        human_scores: List[float]
    ) -> np.ndarray:
        """
        Calibrate LLM scores against human labels

        Uses isotonic regression for calibration
        """
        from sklearn.isotonic import IsotonicRegression

        calibrator = IsotonicRegression(out_of_bounds='clip')
        calibrator.fit(llm_scores, human_scores)

        return calibrator

    def _same_model_family(self, model1: str, model2: str) -> bool:
        """Check if two models are from same family"""
        families = [
            ["gpt-4", "gpt-3.5"],
            ["claude-3", "claude-2"],
            ["gemini-pro", "gemini-ultra"]
        ]

        for family in families:
            if any(m in model1 for m in family) and any(m in model2 for m in family):
                return True

        return False
