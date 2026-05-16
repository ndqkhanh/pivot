/**
 * Tracer utilities for creating and managing spans
 */

import { trace, context, Span, SpanStatusCode } from '@opentelemetry/api';
import type { HarnessAttributes } from './types';

const TRACER_NAME = '@pivot-ai/sdk';

/**
 * Get tracer instance
 */
export function getTracer() {
  return trace.getTracer(TRACER_NAME);
}

/**
 * Get current active span
 */
export function getCurrentSpan(): Span | undefined {
  return trace.getSpan(context.active());
}

/**
 * Set harness attributes on a span
 */
export function setHarnessAttributes(
  span: Span,
  attributes: HarnessAttributes
): void {
  for (const [key, value] of Object.entries(attributes)) {
    if (value !== undefined && value !== null) {
      span.setAttribute(key, value);
    }
  }
}

/**
 * Record an error on a span
 */
export function recordError(span: Span, error: unknown): void {
  span.recordException(error as Error);
  span.setStatus({
    code: SpanStatusCode.ERROR,
    message: error instanceof Error ? error.message : String(error),
  });

  setHarnessAttributes(span, {
    'harness.error': true,
    'harness.error.message': error instanceof Error ? error.message : String(error),
  });
}

/**
 * Wrap an async function with a span
 */
export async function withSpan<T>(
  name: string,
  attributes: HarnessAttributes,
  fn: (span: Span) => Promise<T>
): Promise<T> {
  const tracer = getTracer();
  const span = tracer.startSpan(name);

  setHarnessAttributes(span, attributes);

  try {
    const result = await fn(span);
    span.setStatus({ code: SpanStatusCode.OK });
    return result;
  } catch (error) {
    recordError(span, error);
    throw error;
  } finally {
    span.end();
  }
}
