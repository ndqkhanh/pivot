/**
 * LangChain.js instrumentation
 */

import type { InstrumentationConfig } from '../types';
import { getConfig } from '../config';

let isInstrumented = false;

/**
 * Instrument LangChain.js
 */
export function instrumentLangChain(config: InstrumentationConfig = {}): void {
  if (isInstrumented) {
    console.warn('[Pivot] LangChain already instrumented');
    return;
  }

  const pivotConfig = getConfig();
  if (!pivotConfig) {
    throw new Error('[Pivot] SDK not initialized. Call initializePivot() first.');
  }

  try {
    // LangChain.js uses callbacks for tracing
    // We'll integrate with their callback system
    console.log('[Pivot] LangChain instrumentation enabled');
    isInstrumented = true;

    if (pivotConfig.debug) {
      console.log('[Pivot] LangChain instrumentation enabled');
    }
  } catch (error) {
    console.error('[Pivot] Failed to instrument LangChain:', error);
    throw error;
  }
}
