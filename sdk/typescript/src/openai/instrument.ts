/**
 * OpenAI SDK instrumentation
 */

import type { InstrumentationConfig } from '../types';
import { withSpan, setHarnessAttributes } from '../tracer';
import { getConfig } from '../config';

let isInstrumented = false;

/**
 * Instrument OpenAI SDK
 */
export function instrumentOpenAI(config: InstrumentationConfig = {}): void {
  if (isInstrumented) {
    console.warn('[Pivot] OpenAI already instrumented');
    return;
  }

  const pivotConfig = getConfig();
  if (!pivotConfig) {
    throw new Error('[Pivot] SDK not initialized. Call initializePivot() first.');
  }

  try {
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    const OpenAI = require('openai');

    if (!OpenAI) {
      throw new Error('OpenAI SDK not found');
    }

    patchOpenAI(OpenAI, config);
    isInstrumented = true;

    if (pivotConfig.debug) {
      console.log('[Pivot] OpenAI instrumentation enabled');
    }
  } catch (error) {
    console.error('[Pivot] Failed to instrument OpenAI:', error);
    throw error;
  }
}
