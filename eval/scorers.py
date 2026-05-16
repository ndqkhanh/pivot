"""
Pivot Evaluation Engine - Scorers

Built-in scorer implementations for evaluation tasks.
"""

import re
import json
from typing import Any, Dict
from abc import ABC, abstractmethod


class Scorer(ABC):
    """Base scorer interface."""

    @abstractmethod
    def score(self, output: Any, expected: Any, config: Dict[str, Any]) -> float:
        """Score output against expected, return 0.0-1.0."""
        pass


class ExactScorer(Scorer):
    """Exact match scorer."""

    def score(self, output: Any, expected: Any, config: Dict[str, Any]) -> float:
        case_sensitive = config.get("case_sensitive", False)

        if not case_sensitive:
            output = str(output).lower()
            expected = str(expected).lower()

        return 1.0 if output == expected else 0.0


class RegexScorer(Scorer):
    """Regex pattern matcher."""

    def score(self, output: Any, expected: Any, config: Dict[str, Any]) -> float:
        pattern = config["pattern"]
        flags = 0

        if "IGNORECASE" in config.get("flags", []):
            flags |= re.IGNORECASE

        return 1.0 if re.match(pattern, str(output), flags) else 0.0


class JSONSchemaScorer(Scorer):
    """JSON schema validator."""

    def score(self, output: Any, expected: Any, config: Dict[str, Any]) -> float:
        try:
            # Parse output as JSON
            if isinstance(output, str):
                output = json.loads(output)

            # Simple schema validation
            schema = config["schema"]
            return 1.0 if self._validate_schema(output, schema) else 0.0
        except:
            return 0.0

    def _validate_schema(self, data: Any, schema: Dict[str, Any]) -> bool:
        """Simple schema validation."""
        if schema.get("type") == "object":
            if not isinstance(data, dict):
                return False

            # Check required fields
            required = schema.get("required", [])
            if not all(k in data for k in required):
                return False

            # Check properties
            properties = schema.get("properties", {})
            for key, prop_schema in properties.items():
                if key in data:
                    if not self._validate_schema(data[key], prop_schema):
                        return False

            return True

        elif schema.get("type") == "string":
            return isinstance(data, str)

        elif schema.get("type") == "integer":
            return isinstance(data, int)

        elif schema.get("type") == "number":
            return isinstance(data, (int, float))

        return True


# Scorer registry
SCORERS = {
    "exact": ExactScorer(),
    "regex": RegexScorer(),
    "json_schema": JSONSchemaScorer(),
}


def get_scorer(scorer_type: str) -> Scorer:
    """Get scorer by type."""
    if scorer_type not in SCORERS:
        raise ValueError(f"Unknown scorer type: {scorer_type}")
    return SCORERS[scorer_type]
