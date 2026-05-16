package main

import (
	"context"
	"fmt"
	"log"

	"go.opentelemetry.io/collector/pdata/ptrace"
)

// TraceService implements the OTLP trace service
type TraceService struct {
	gateway *Gateway
}

// Export handles incoming trace data
func (s *TraceService) Export(ctx context.Context, req ptrace.Traces) (ptrace.ExportResponse, error) {
	spanCount := 0

	// Process each resource span
	for i := 0; i < req.ResourceSpans().Len(); i++ {
		rs := req.ResourceSpans().At(i)

		// Process each scope span
		for j := 0; j < rs.ScopeSpans().Len(); j++ {
			ss := rs.ScopeSpans().At(j)

			// Process each span
			for k := 0; k < ss.Spans().Len(); k++ {
				span := ss.Spans().At(k)
				spanCount++

				// Extract harness.* attributes
				attrs := span.Attributes()

				var runID, policyVersion, policyDecision, stakeholderPrincipal string

				attrs.Range(func(k string, v ptrace.Value) bool {
					switch k {
					case "harness.run_id":
						runID = v.Str()
					case "harness.policy_version":
						policyVersion = v.Str()
					case "harness.policy_decision":
						policyDecision = v.Str()
					case "harness.stakeholder.principal":
						stakeholderPrincipal = v.Str()
					}
					return true
				})

				// Log span info
				log.Printf("Received span: trace_id=%s, span_id=%s, run_id=%s, principal=%s",
					span.TraceID().String(),
					span.SpanID().String(),
					runID,
					stakeholderPrincipal,
				)

				// TODO: Policy enforcement
				if s.gateway.config.EnablePolicyEnforcement {
					// Evaluate policy
					decision := s.evaluatePolicy(span, stakeholderPrincipal)
					if decision == "deny" {
						log.Printf("Policy denied span: %s", span.SpanID().String())
						// In production, would return error or modify span
					}
				}

				// TODO: Write to ClickHouse
				if err := s.writeToClickHouse(span); err != nil {
					log.Printf("Failed to write span to ClickHouse: %v", err)
				}
			}
		}
	}

	log.Printf("Processed %d spans", spanCount)

	return ptrace.NewExportResponse(), nil
}

// evaluatePolicy evaluates policy for a span
func (s *TraceService) evaluatePolicy(span ptrace.Span, principal string) string {
	// TODO: Call OPA policy engine
	// For now, allow all
	return "allow"
}

// writeToClickHouse writes span to ClickHouse
func (s *TraceService) writeToClickHouse(span ptrace.Span) error {
	// TODO: Implement ClickHouse writer
	return nil
}
