"""
Counterfactual Replay Engine

Implements "what-if" analysis by replaying agent runs with interventions:
- Policy swaps
- Model swaps
- Step-level overrides
- Divergence detection
- Causal effect estimation
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from enum import Enum


class InterventionType(Enum):
    """Types of interventions for counterfactual replay"""
    POLICY_SWAP = "policy_swap"
    MODEL_SWAP = "model_swap"
    STEP_OVERRIDE = "step_override"
    PARAMETER_CHANGE = "parameter_change"


@dataclass
class Intervention:
    """Specification for a counterfactual intervention"""
    type: InterventionType
    target: str  # What to intervene on (policy name, model name, step ID)
    value: Any  # New value to use
    condition: Optional[Dict[str, Any]] = None  # When to apply (optional)


@dataclass
class CounterfactualResult:
    """Result of counterfactual replay"""
    original_run_id: str
    intervention: Intervention
    new_run_id: str
    first_divergence_step: Optional[int]
    original_score: float
    counterfactual_score: float
    causal_effect: float  # ACE: Average Causal Effect
    divergence_points: List[int]
    metadata: Dict[str, Any]


class CounterfactualEngine:
    """
    Engine for counterfactual replay with causal inference

    Based on Pearl's do-calculus and identifiability conditions
    """

    def __init__(self, storage_backend):
        self.storage = storage_backend

    def replay_with_intervention(
        self,
        original_run_id: str,
        intervention: Intervention
    ) -> CounterfactualResult:
        """
        Replay a run with an intervention

        Args:
            original_run_id: ID of original run to replay
            intervention: Intervention specification

        Returns:
            CounterfactualResult with divergence analysis
        """
        # Load original run
        original_run = self.storage.load_run(original_run_id)

        # Apply intervention and replay
        new_run = self._replay_with_intervention(original_run, intervention)

        # Detect divergence
        divergence = self._detect_divergence(original_run, new_run)

        # Calculate causal effect
        ace = self._calculate_ace(original_run, new_run)

        return CounterfactualResult(
            original_run_id=original_run_id,
            intervention=intervention,
            new_run_id=new_run.id,
            first_divergence_step=divergence.first_step,
            original_score=original_run.score,
            counterfactual_score=new_run.score,
            causal_effect=ace,
            divergence_points=divergence.all_steps,
            metadata={"identifiable": divergence.is_identifiable}
        )
