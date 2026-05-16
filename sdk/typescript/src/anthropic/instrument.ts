/**
 * Anthropic SDK instrumentation
 */

import type { InstrumentationConfig } from '../types';
import { withSpan } from '../tracer';
import { getConfig } from '../config';

let isInstrumented = false;

/**
 * Instrument Anthropic SDK
 */
export function instrumentAnthropic(config: InstrumentationConfig = {}): void {
  if (isInstrumented) {
    console.warn('[Pivot] Anthropic already instrumented');
    return;
  }

  const pivotConfig = getConfig();
  if (!pivotConfig) {
    throw new Error('[Pivot] SDK not initialized. Call initializePivot() first.');
  }

  try {
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    const Anthropic = require('@anthropic-ai/sdk');

    if (!Anthropic) {
      throw new Error('Anthropic SDK not found');
    }

    patchAnthropic(Anthropic, config);
    isInstrumented = true;

    if (pivotConfig.debug) {
      console.log('[Pivot] Anthropic instrumentation enabled');
    }
  } catch (error) {
    console.error('[Pivot] Failed to instrument Anthropic:', error);
    throw error;
  }
}

function patchAnthropic(Anthropic: any, config: InstrumentationConfig): void {
  const originalCreate = Anthropic.prototype.messages?.create;

  if (!originalCreate) {
    throw new Error('Anthropic messages.create not found');
  }

  Anthropic.prototype.messages.create = async function (
    this: any,
    params: any
  ): Promise<any> {
    const model = params.model || 'unknown';

    return withSpan(
      'anthropic.messages.create',
      {
        'harness.actor': 'assistant',
        'harness.kind': 'model_call',
        'harness.principal': model,
        'harness.model.provider': 'anthropic',
        'harness.model.name': model,
      },
      async (span) => {
        const startTime = Date.now();

        try {
          const response = await originalCreate.call(this, params);
          const duration = Date.now() - startTime;

          // Extract usage
          const usage = response.usage;
          if (usage) {
            span.setAttribute('harness.model.input_tokens', usage.input_tokens);
            span.setAttribute('harness.model.output_tokens', usage.output_tokens);
          }

          span.setAttribute('duration_ms', duration);

          return response;
        } catch (error) {
          throw error;
        }
      }
    );
  };
}
