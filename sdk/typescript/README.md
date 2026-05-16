# @pivot-ai/sdk - TypeScript SDK

TypeScript SDK for the Pivot AI Agent Reliability Platform.

## Installation

```bash
npm install @pivot-ai/sdk
```

## Quick Start

```typescript
import { initializePivot, instrumentOpenAI, instrumentAnthropic } from '@pivot-ai/sdk';

// Initialize Pivot SDK
initializePivot({
  endpoint: 'http://localhost:4317',
  serviceName: 'my-agent',
  debug: true
});

// Instrument SDKs
instrumentOpenAI();
instrumentAnthropic();

// Your agent code runs normally - traces are automatically captured
import OpenAI from 'openai';
const openai = new OpenAI();

const response = await openai.chat.completions.create({
  model: 'gpt-4',
  messages: [{ role: 'user', content: 'Hello!' }]
});
```

## Features

- **Auto-instrumentation** for OpenAI and Anthropic SDKs
- **OpenTelemetry integration** with OTLP export
- **harness.* attributes** for agent-specific metadata
- **Zero-code changes** to existing agent code
- **TypeScript support** with full type definitions

## Configuration

```typescript
interface PivotConfig {
  endpoint?: string;        // OTLP endpoint (default: http://localhost:4317)
  protocol?: 'grpc' | 'http'; // Transport protocol (default: grpc)
  serviceName?: string;     // Service name (default: pivot-agent)
  debug?: boolean;          // Enable debug logging (default: false)
  attributes?: Record<string, string | number | boolean>; // Custom attributes
}
```

## License

Apache 2.0
