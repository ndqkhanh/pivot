"""
Goal Management System for Pivot Project

Implements /goal command similar to Claude Code:
- Set persistent goals across sessions
- Track goal progress
- Display goal status
- Auto-resume from last session
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
import json
from pathlib import Path


@dataclass
class Goal:
    """A project goal"""
    id: str
    text: str
    created_at: datetime
    updated_at: datetime
    status: str  # "active", "completed", "paused"
    progress: float  # 0.0 to 1.0
    tasks: List[str]
    metadata: dict


class GoalManager:
    """
    Manages project goals with persistence

    Features:
    - Set and track goals
    - Persist across sessions
    - Progress tracking
    - Task breakdown
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.goal_file = project_root / ".pivot" / "goal.json"
        self.goal_file.parent.mkdir(parents=True, exist_ok=True)
        self.current_goal: Optional[Goal] = None
        self._load_goal()

    def set_goal(self, goal_text: str) -> Goal:
        """
        Set a new goal

        Args:
            goal_text: Goal description

        Returns:
            Created goal
        """
        goal = Goal(
            id=self._generate_id(),
            text=goal_text,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status="active",
            progress=0.0,
            tasks=[],
            metadata={}
        )

        self.current_goal = goal
        self._save_goal()

        return goal

    def update_progress(self, progress: float, completed_tasks: List[str] = None):
        """Update goal progress"""
        if not self.current_goal:
            return

        self.current_goal.progress = progress
        self.current_goal.updated_at = datetime.now()

        if completed_tasks:
            self.current_goal.tasks.extend(completed_tasks)

        self._save_goal()

    def get_goal(self) -> Optional[Goal]:
        """Get current active goal"""
        return self.current_goal

    def complete_goal(self):
        """Mark current goal as completed"""
        if self.current_goal:
            self.current_goal.status = "completed"
            self.current_goal.progress = 1.0
            self.current_goal.updated_at = datetime.now()
            self._save_goal()

    def clear_goal(self):
        """Clear current goal"""
        self.current_goal = None
        if self.goal_file.exists():
            self.goal_file.unlink()

    def format_status(self) -> str:
        """Format goal status for display"""
        if not self.current_goal:
            return "No active goal"

        progress_bar = self._progress_bar(self.current_goal.progress)
        tasks_summary = f"{len(self.current_goal.tasks)} tasks completed"

        return f"""
◎ Goal: {self.current_goal.text}
  Status: {self.current_goal.status}
  Progress: {progress_bar} {self.current_goal.progress:.0%}
  {tasks_summary}
  Last updated: {self.current_goal.updated_at.strftime('%Y-%m-%d %H:%M')}
"""

    def _progress_bar(self, progress: float, width: int = 20) -> str:
        """Generate progress bar"""
        filled = int(progress * width)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"

    def _generate_id(self) -> str:
        """Generate unique goal ID"""
        import uuid
        return f"goal_{uuid.uuid4().hex[:8]}"

    def _save_goal(self):
        """Save goal to disk"""
        if not self.current_goal:
            return

        data = {
            "id": self.current_goal.id,
            "text": self.current_goal.text,
            "created_at": self.current_goal.created_at.isoformat(),
            "updated_at": self.current_goal.updated_at.isoformat(),
            "status": self.current_goal.status,
            "progress": self.current_goal.progress,
            "tasks": self.current_goal.tasks,
            "metadata": self.current_goal.metadata
        }

        with open(self.goal_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _load_goal(self):
        """Load goal from disk"""
        if not self.goal_file.exists():
            return

        try:
            with open(self.goal_file, 'r') as f:
                data = json.load(f)

            self.current_goal = Goal(
                id=data["id"],
                text=data["text"],
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"]),
                status=data["status"],
                progress=data["progress"],
                tasks=data["tasks"],
                metadata=data["metadata"]
            )
        except Exception as e:
            print(f"Failed to load goal: {e}")
            self.current_goal = None


# CLI Command Handler
def handle_goal_command(args: List[str], project_root: Path) -> str:
    """
    Handle /goal command

    Usage:
        /goal <text>              - Set new goal
        /goal status              - Show current goal
        /goal complete            - Mark goal as completed
        /goal clear               - Clear current goal
    """
    manager = GoalManager(project_root)

    if not args:
        # Show status
        return manager.format_status()

    command = args[0].lower()

    if command == "status":
        return manager.format_status()

    elif command == "complete":
        manager.complete_goal()
        return "✅ Goal marked as completed!"

    elif command == "clear":
        manager.clear_goal()
        return "Goal cleared"

    else:
        # Set new goal (all args as goal text)
        goal_text = " ".join(args)
        goal = manager.set_goal(goal_text)
        return f"""
⎿ Goal set: {goal.text}

  ◎ Goal is now active and will persist across sessions
  ◎ Use /goal status to check progress
  ◎ Use /goal complete when done
"""


# Example usage in REPL
if __name__ == "__main__":
    from pathlib import Path

    # Example: Set goal
    result = handle_goal_command(
        ["Continue", "from", "last", "session", "until", "finish", "all"],
        Path(".")
    )
    print(result)

    # Example: Check status
    manager = GoalManager(Path("."))
    print(manager.format_status())
