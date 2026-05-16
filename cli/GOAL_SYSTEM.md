# Goal Management System

Persistent goal tracking for Pivot project, similar to Claude Code's `/goal` command.

## Features

- **Persistent Goals** - Goals survive across sessions
- **Progress Tracking** - Visual progress bars and task completion
- **Status Display** - Clear goal status with timestamps
- **Auto-Resume** - Automatically loads last goal on startup

## Usage

### Set a Goal

```bash
/goal Continue from last session until finish all for me. Remember to push to github each phase
```

Output:
```
⎿ Goal set: Continue from last session until finish all for me. Remember to push to github each phase

  ◎ Goal is now active and will persist across sessions
  ◎ Use /goal status to check progress
  ◎ Use /goal complete when done
```

### Check Status

```bash
/goal status
```

Output:
```
◎ Goal: Continue from last session until finish all for me
  Status: active
  Progress: [████████████░░░░░░░░] 60%
  12 tasks completed
  Last updated: 2026-05-16 22:45
```

### Mark Complete

```bash
/goal complete
```

### Clear Goal

```bash
/goal clear
```

## Integration

### In Python Code

```python
from cli.goal_manager import GoalManager
from pathlib import Path

# Initialize
manager = GoalManager(Path("."))

# Set goal
goal = manager.set_goal("Implement Phase 3 features")

# Update progress
manager.update_progress(0.5, completed_tasks=["Task 1", "Task 2"])

# Check status
print(manager.format_status())

# Complete
manager.complete_goal()
```

### In CLI/REPL

```python
from cli.goal_manager import handle_goal_command

# Handle command
result = handle_goal_command(["status"], Path("."))
print(result)
```

## Storage

Goals are stored in `.pivot/goal.json`:

```json
{
  "id": "goal_a1b2c3d4",
  "text": "Continue from last session until finish all",
  "created_at": "2026-05-16T22:30:00",
  "updated_at": "2026-05-16T22:45:00",
  "status": "active",
  "progress": 0.6,
  "tasks": ["Task 1", "Task 2"],
  "metadata": {}
}
```

## Status Indicators

- `◎` - Active goal indicator
- `⎿` - Goal set confirmation
- `✅` - Goal completed
- `[████░░░░]` - Progress bar

## Example Workflow

```bash
# Start new session
$ /goal Implement all Phase 3 components and push to GitHub

⎿ Goal set: Implement all Phase 3 components and push to GitHub
  ◎ Goal is now active

# Work on tasks...
# (Progress automatically tracked)

# Check progress
$ /goal status

◎ Goal: Implement all Phase 3 components and push to GitHub
  Status: active
  Progress: [████████████████████] 100%
  15 tasks completed

# Mark complete
$ /goal complete

✅ Goal marked as completed!
```

## Benefits

1. **Persistence** - Never lose track of what you're working on
2. **Clarity** - Always know the current objective
3. **Progress** - Visual feedback on completion
4. **Resumability** - Pick up exactly where you left off

## License

Apache 2.0
