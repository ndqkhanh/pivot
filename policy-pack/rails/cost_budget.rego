# Cost Budget Rail
# Enforces spending limits per run and per day

package pivot.rails.cost_budget

import future.keywords.if

# Deny if per-run budget exceeded
deny[msg] if {
    input.run_cost_usd > input.policy.budgets.cost.max_per_run_usd
    msg := sprintf("Cost budget exceeded: $%.2f > $%.2f",
                   [input.run_cost_usd, input.policy.budgets.cost.max_per_run_usd])
}

# Deny if daily budget exceeded
deny[msg] if {
    input.daily_cost_usd > input.policy.budgets.cost.max_per_day_usd
    msg := sprintf("Daily cost budget exceeded: $%.2f > $%.2f",
                   [input.daily_cost_usd, input.policy.budgets.cost.max_per_day_usd])
}

# Deny if token budget exceeded
deny[msg] if {
    input.run_tokens > input.policy.budgets.tokens.max_per_run
    msg := sprintf("Token budget exceeded: %d > %d",
                   [input.run_tokens, input.policy.budgets.tokens.max_per_run])
}
