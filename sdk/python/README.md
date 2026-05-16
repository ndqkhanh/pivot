# Pivot Python SDK

Production-grade Python SDK for Pivot Agent Reliability Harness.

## Installation

```bash
pip install pivot-sdk
```

## Quick Start

```python
from pivot import initialize, instrument_openai

# Initialize Pivot
config = initialize()

# Instrument OpenAI
instrument_openai(stakeholder_principal="user_alice")

# Use OpenAI as normal - automatically traced!
import openai
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}],
    seed=42  # For deterministic replay
)
```

## Features

- **Auto-instrumentation** for OpenAI and Anthropic
- **OpenTelemetry-native** with harness.* extensions
- **Deterministic replay** support with provenance tracking
- **Policy-aware** with stakeholder principal tracking
- **Zero-code** instrumentation

## Supported Frameworks

- ✅ OpenAI SDK
- ✅ Anthropic SDK
- ✅ LangGraph
- ✅ CrewAI
- 🔄 AutoGen (coming soon)

## Configuration

```python
from pivot import PivotConfig, initialize

config = PivotConfig(
    endpoint="http://localhost:4317",  # Gateway endpoint
    run_id="custom-run-id",            # Optional: auto-generated if not provided
    policy_version="v1.0",             # Policy version
    stakeholder_principal="user_alice", # Principal making requests
    enable_replay=True                  # Enable replay provenance
)

initialize(config)
```

## Examples

### Basic Usage

```python
from pivot import initialize, instrument_openai
import openai

# Initialize
initialize()
instrument_openai()

# Use OpenAI - automatically traced
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "What is 2+2?"}]
)
```

### With Stakeholder Principal

```python
from pivot import initialize, instrument_openai

# Initialize with principal
initialize()
instrument_openai(stakeholder_principal="user_bob")

# All requests tagged with principal
response = openai.ChatCompletion.create(...)
```

### Deterministic Replay

```python
# Use seed for deterministic replay
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}],
    seed=42,           # Deterministic seed
    temperature=0.7    # Fixed temperature
)
```

## Development

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linters
ruff check .
black .
mypy .
```

## License

Apache 2.0
