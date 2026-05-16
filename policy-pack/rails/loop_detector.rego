# Loop Detection Rail
# Detects and prevents infinite loops

package pivot.rails.loop_detector

import future.keywords.if

# Deny if same action repeated too many times
deny[msg] if {
    action_repetition_count(input.recent_actions, input.current_action) > 3
    msg := "Loop detected: same action repeated >3 times"
}

# Deny if oscillating between two actions
deny[msg] if {
    is_oscillating(input.recent_actions)
    msg := "Loop detected: oscillating between two actions"
}

# Helper: count action repetitions
action_repetition_count(recent, current) = count if {
    matching := [a | a := recent[_]; a.name == current.name]
    count := count(matching)
}

# Helper: detect oscillation
is_oscillating(actions) if {
    count(actions) >= 4
    actions[0].name == actions[2].name
    actions[1].name == actions[3].name
    actions[0].name != actions[1].name
}
