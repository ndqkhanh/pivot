/**
 * Core types for Pivot TypeScript SDK
 */

export interface PivotConfig {
  /** OTLP endpoint URL (default: http://localhost:4317) */
  endpoint?: string;
  /** Transport protocol (default: grpc) */
  protocol?: 'grpc' | 'http';
  /** Service name for traces */
  serviceName?: string;
  /** Enable debug logging */
  debug?: boolean;
  /** Custom attributes to add to all spans */
  attributes?: Record<string, string | number | boolean>;
}

export interface InstrumentationConfig {
  /** Enable/disable instrumentation */
  enabled?: boolean;
  /** Capture request/response bodies */
  captureContent?: boolean;
  /** Maximum content length to capture (bytes) */
  maxContentLength?: number;
}

export interface HarnessAttributes {
  /** Agent actor (user, assistant, tool, system) */
  'harness.actor'?: string;
  /** Span kind (model_call, tool_call, agent_step) */
  'harness.kind'?: string;
  /** Principal entity (model name, tool name) */
  'harness.principal'?: string;
  /** Model provider (openai, anthropic) */
  'harness.model.provider'?: string;
  /** Model name */
  'harness.model.name'?: string;
  /** Input tokens */
  'harness.model.input_tokens'?: number;
  /** Output tokens */
  'harness.model.output_tokens'?: number;
  /** Cost in USD */
  'harness.model.cost_usd'?: number;
  /** Tool name */
  'harness.tool.name'?: string;
  /** Tool input schema */
  'harness.tool.input_schema'?: string;
  /** Tool output */
  'harness.tool.output'?: string;
  /** Error flag */
  'harness.error'?: boolean;
  /** Error message */
  'harness.error.message'?: string;
}
