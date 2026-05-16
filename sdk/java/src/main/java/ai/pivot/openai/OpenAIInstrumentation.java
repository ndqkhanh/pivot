package ai.pivot.openai;

import ai.pivot.core.PivotSDK;
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.StatusCode;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.context.Scope;

/**
 * OpenAI SDK instrumentation for Java
 */
public final class OpenAIInstrumentation {
    private static volatile boolean instrumented = false;

    private OpenAIInstrumentation() {
        // Prevent instantiation
    }

    /**
     * Instrument OpenAI SDK
     */
    public static synchronized void instrument() {
        if (instrumented) {
            System.err.println("[Pivot] OpenAI already instrumented");
            return;
        }

        if (PivotSDK.getConfig() == null) {
            throw new IllegalStateException("Pivot SDK not initialized");
        }

        // Instrumentation logic would go here
        // This is a simplified version - full implementation would use
        // bytecode instrumentation or proxy patterns

        instrumented = true;

        if (PivotSDK.getConfig().isDebug()) {
            System.out.println("[Pivot] OpenAI instrumentation enabled");
        }
    }

    /**
     * Create a span for OpenAI API call
     */
    public static Span createSpan(String model) {
        Tracer tracer = PivotSDK.getTracer();
        Span span = tracer.spanBuilder("openai.chat.completions.create")
            .startSpan();

        span.setAttribute("harness.actor", "assistant");
        span.setAttribute("harness.kind", "model_call");
        span.setAttribute("harness.principal", model);
        span.setAttribute("harness.model.provider", "openai");
        span.setAttribute("harness.model.name", model);

        return span;
    }

    /**
     * Record usage on span
     */
    public static void recordUsage(Span span, int inputTokens, int outputTokens) {
        span.setAttribute("harness.model.input_tokens", inputTokens);
        span.setAttribute("harness.model.output_tokens", outputTokens);

        // Estimate cost
        double cost = (inputTokens * 0.000001) + (outputTokens * 0.000002);
        span.setAttribute("harness.model.cost_usd", cost);
    }
}
