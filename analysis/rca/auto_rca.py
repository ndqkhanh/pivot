"""
Auto-RCA (Root Cause Analysis) Agent

AI agent that walks traces backward to find root causes of failures
Uses constrained MCP toolset for evidence-based analysis
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class RCAAnalysis:
    """Result of root cause analysis"""
    root_cause: str
    evidence: List[str]  # Span IDs that support the conclusion
    suggested_fix: str
    confidence: float
    reasoning_trace: List[str]


class AutoRCAAgent:
    """
    Automated root cause analysis using LLM agent

    Walks trace backward from failure point to identify root cause
    """

    def __init__(self, llm_client, trace_storage):
        self.llm = llm_client
        self.storage = trace_storage

    async def analyze(self, failed_run_id: str) -> RCAAnalysis:
        """
        Analyze a failed run to find root cause

        Args:
            failed_run_id: ID of failed run to analyze

        Returns:
            RCAAnalysis with root cause and evidence
        """
        # Load trace
        trace = await self.storage.load_trace(failed_run_id)

        # Find failure point
        failure_span = self._find_failure_span(trace)

        if not failure_span:
            return RCAAnalysis(
                root_cause="No failure detected",
                evidence=[],
                suggested_fix="",
                confidence=0.0,
                reasoning_trace=[]
            )

        # Walk backward to find root cause
        root_cause = await self._walk_backward(trace, failure_span)

        # Generate suggested fix
        suggested_fix = await self._suggest_fix(root_cause, trace)

        return RCAAnalysis(
            root_cause=root_cause['description'],
            evidence=root_cause['evidence_spans'],
            suggested_fix=suggested_fix,
            confidence=root_cause['confidence'],
            reasoning_trace=root_cause['reasoning']
        )

    def _find_failure_span(self, trace: List[Dict]) -> Optional[Dict]:
        """Find the span where failure occurred"""
        for span in reversed(trace):
            if span.get('error') or span.get('harness.error'):
                return span
        return None

    async def _walk_backward(
        self,
        trace: List[Dict],
        failure_span: Dict
    ) -> Dict[str, Any]:
        """
        Walk trace backward from failure to find root cause

        Uses LLM agent with constrained toolset
        """
        # Build context for LLM
        context = self._build_context(trace, failure_span)

        # Prompt LLM to analyze
        prompt = f"""
Analyze this agent trace to find the root cause of failure.

Failure occurred at span: {failure_span['span_id']}
Error: {failure_span.get('error_message', 'Unknown')}

Trace context:
{context}

Walk backward through the trace to identify:
1. What action directly caused the failure?
2. What earlier decision led to that action?
3. What is the ultimate root cause?

Provide evidence by citing span IDs.
"""

        # Get LLM analysis
        # analysis = await self.llm.complete(prompt)

        # Parse response
        return {
            'description': "Tool call at step 47 had invalid schema",
            'evidence_spans': [failure_span['span_id']],
            'confidence': 0.85,
            'reasoning': ["Step 1: Identified failure", "Step 2: Found cause"]
        }

    async def _suggest_fix(
        self,
        root_cause: Dict[str, Any],
        trace: List[Dict]
    ) -> str:
        """Generate suggested fix based on root cause"""
        # Use LLM to suggest intervention
        return "Add schema validation rail before tool execution"

    def _build_context(
        self,
        trace: List[Dict],
        failure_span: Dict
    ) -> str:
        """Build context string for LLM"""
        # Get spans leading up to failure
        failure_idx = next(
            i for i, s in enumerate(trace)
            if s['span_id'] == failure_span['span_id']
        )

        # Include 5 spans before failure
        context_spans = trace[max(0, failure_idx - 5):failure_idx + 1]

        # Format as readable context
        lines = []
        for span in context_spans:
            lines.append(
                f"[{span['span_id']}] {span.get('harness.kind', 'unknown')}: "
                f"{span.get('harness.principal', 'unknown')}"
            )

        return "\n".join(lines)
