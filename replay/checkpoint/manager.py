"""
Checkpoint system for replay fork points

Enables branching from specific points in agent execution
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass
class Checkpoint:
    """A checkpoint in agent execution"""
    id: str
    run_id: str
    step_number: int
    timestamp: datetime
    state: Dict[str, Any]  # Serialized agent state
    context: Dict[str, Any]  # Conversation context
    metadata: Dict[str, Any]


class CheckpointManager:
    """Manages checkpoints for replay branching"""

    def __init__(self, storage_backend):
        self.storage = storage_backend

    def create_checkpoint(
        self,
        run_id: str,
        step_number: int,
        state: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Checkpoint:
        """
        Create a checkpoint at current execution point

        Args:
            run_id: Run identifier
            step_number: Current step number
            state: Agent state to save
            context: Conversation context

        Returns:
            Created checkpoint
        """
        checkpoint = Checkpoint(
            id=self._generate_id(),
            run_id=run_id,
            step_number=step_number,
            timestamp=datetime.utcnow(),
            state=state,
            context=context,
            metadata={}
        )

        self.storage.save_checkpoint(checkpoint)
        return checkpoint

    def restore_checkpoint(self, checkpoint_id: str) -> Checkpoint:
        """Load checkpoint for replay"""
        return self.storage.load_checkpoint(checkpoint_id)

    def list_checkpoints(self, run_id: str) -> List[Checkpoint]:
        """List all checkpoints for a run"""
        return self.storage.list_checkpoints(run_id)

    def _generate_id(self) -> str:
        """Generate unique checkpoint ID"""
        import uuid
        return f"ckpt_{uuid.uuid4().hex[:12]}"
