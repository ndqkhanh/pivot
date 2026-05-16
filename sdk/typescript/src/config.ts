/**
 * Global configuration for Pivot SDK
 */

import { NodeTracerProvider } from '@opentelemetry/sdk-trace-node';
import { Resource } from '@opentelemetry/resources';
import { SEMRESATTRS_SERVICE_NAME } from '@opentelemetry/semantic-conventions';
import { OTLPTraceExporter as GrpcExporter } from '@opentelemetry/exporter-trace-otlp-grpc';
import { OTLPTraceExporter as HttpExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { BatchSpanProcessor } from '@opentelemetry/sdk-trace-node';
import type { PivotConfig } from './types';

let provider: NodeTracerProvider | null = null;
let config: Required<PivotConfig> | null = null;

const DEFAULT_CONFIG: Required<PivotConfig> = {
  endpoint: 'http://localhost:4317',
  protocol: 'grpc',
  serviceName: 'pivot-agent',
  debug: false,
  attributes: {},
};

/**
 * Initialize Pivot SDK with configuration
 */
export function initializePivot(userConfig: PivotConfig = {}): void {
  if (provider) {
    console.warn('Pivot SDK already initialized');
    return;
  }

  config = { ...DEFAULT_CONFIG, ...userConfig };

  // Create resource with service name and custom attributes
  const resource = Resource.default().merge(
    new Resource({
      [SEMRESATTRS_SERVICE_NAME]: config.serviceName,
      ...config.attributes,
    })
  );

  // Create tracer provider
  provider = new NodeTracerProvider({
    resource,
  });

  // Create OTLP exporter based on protocol
  const exporter =
    config.protocol === 'grpc'
      ? new GrpcExporter({ url: config.endpoint })
      : new HttpExporter({ url: config.endpoint });

  // Add batch span processor
  provider.addSpanProcessor(new BatchSpanProcessor(exporter));

  // Register provider
  provider.register();

  if (config.debug) {
    console.log('[Pivot] Initialized with config:', config);
  }
}

/**
 * Get current configuration
 */
export function getConfig(): Required<PivotConfig> | null {
  return config;
}

/**
 * Get tracer provider
 */
export function getProvider(): NodeTracerProvider | null {
  return provider;
}

/**
 * Shutdown Pivot SDK
 */
export async function shutdown(): Promise<void> {
  if (provider) {
    await provider.shutdown();
    provider = null;
    config = null;
  }
}
