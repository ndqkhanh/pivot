/**
 * OpenAI SDK patching logic
 */

import type { InstrumentationConfig } from '../types';
import { withSpan } from '../tracer';

export function patchOpenAI(OpenAI: any, config: InstrumentationConfig): void {
  const originalCreate = OpenAI.prototype.chat?.completions?.create;

  if (!originalCreate) {
    throw new Error('OpenAI chat.completions.create not found');
  }

  OpenAI.prototype.chat.completions.create = async function (
    this: any,
    params: any
  ): Promise<any> {
    const model = params.model || 'unknown';

    return withSpan(
      'openai.chat.completions.create',
      {
        'harness.actor': 'assistant',
        'harness.kind': 'model_call',
        'harness.principal': model,
        'harness.model.provider': 'openai',
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
            span.setAttribute('harness.model.input_tokens', usage.prompt_tokens);
            span.setAttribute('harness.model.output_tokens', usage.completion_tokens);

            // Estimate cost (simplified)
            const cost = estimateCost(model, usage);
            span.setAttribute('harness.model.cost_usd', cost);
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

function estimateCost(model: string, usage: any): number {
  // Simplified cost estimation
  const inputCost = usage.prompt_tokens * 0.000001;
  const outputCost = usage.completion_tokens * 0.000002;
  return inputCost + outputCost;
}
