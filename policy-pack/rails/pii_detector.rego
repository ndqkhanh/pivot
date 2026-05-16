# PII Detection Rail
# Detects and blocks personally identifiable information

package pivot.rails.pii_detector

import future.keywords.if

# Deny if SSN pattern detected
deny[msg] if {
    regex.match(`\d{3}-\d{2}-\d{4}`, input.content)
    msg := "PII detected: SSN pattern found"
}

# Deny if email detected (non-owner only)
deny[msg] if {
    regex.match(`[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`, input.content)
    input.stakeholder.principal_type != "owner"
    msg := "PII detected: Email found (non-owner)"
}

# Deny if credit card pattern detected
deny[msg] if {
    regex.match(`\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}`, input.content)
    msg := "PII detected: Credit card pattern found"
}

# Deny if phone number detected
deny[msg] if {
    regex.match(`\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}`, input.content)
    input.stakeholder.principal_type != "owner"
    msg := "PII detected: Phone number found"
}
