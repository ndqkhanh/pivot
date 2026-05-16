# Rate Limiting Rail
# Enforces per-principal, per-tool rate limits

package pivot.rails.rate_limiter

import future.keywords.if

# Deny if rate limit exceeded
deny[msg] if {
    limit := get_rate_limit(input.stakeholder.principal, input.tool.name)
    calls_in_window := count_recent_calls(input.stakeholder.principal, input.tool.name, 60)
    calls_in_window >= limit
    msg := sprintf("Rate limit exceeded: %d calls/min (limit: %d)",
                   [calls_in_window, limit])
}

# Get rate limit for principal and tool
get_rate_limit(principal, tool) = limit if {
    limit_config := input.policy.budgets.rate_limits[_]
    limit_config.principal == principal
    limit_config.tool == tool
    limit := limit_config.max_calls_per_minute
}

# Default rate limit if not specified
get_rate_limit(principal, tool) = 60 if {
    not get_rate_limit(principal, tool)
}

# Count recent calls (would query from storage in production)
count_recent_calls(principal, tool, window_seconds) = count if {
    # Placeholder - would query actual call history
    count := 0
}
