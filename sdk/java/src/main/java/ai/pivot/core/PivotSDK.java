package ai.pivot.core;

import io.opentelemetry.api.OpenTelemetry;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.api.trace.TracerProvider;
import io.opentelemetry.sdk.OpenTelemetrySdk;
import io.opentelemetry.sdk.resources.Resource;
import io.opentelemetry.sdk.trace.SdkTracerProvider;
import io.opentelemetry.sdk.trace.export.BatchSpanProcessor;
import io.opentelemetry.exporter.otlp.trace.OtlpGrpcSpanExporter;
import io.opentelemetry.semconv.ResourceAttributes;

/**
 * Main entry point for Pivot SDK initialization
 */
public final class PivotSDK {
    private static volatile OpenTelemetry openTelemetry;
    private static volatile PivotConfig config;
    private static final String INSTRUMENTATION_NAME = "ai.pivot.sdk";

    private PivotSDK() {
        // Prevent instantiation
    }

    /**
     * Initialize Pivot SDK with configuration
     */
    public static synchronized void initialize(PivotConfig config) {
        if (openTelemetry != null) {
            System.err.println("[Pivot] SDK already initialized");
            return;
        }

        PivotSDK.config = config;

        // Build resource with service name
        Resource resource = Resource.getDefault()
            .merge(Resource.create(
                io.opentelemetry.api.common.Attributes.of(
                    ResourceAttributes.SERVICE_NAME, config.getServiceName()
                )
            ));

        // Create OTLP exporter
        OtlpGrpcSpanExporter spanExporter = OtlpGrpcSpanExporter.builder()
            .setEndpoint(config.getEndpoint())
            .build();

        // Create tracer provider
        SdkTracerProvider tracerProvider = SdkTracerProvider.builder()
            .setResource(resource)
            .addSpanProcessor(BatchSpanProcessor.builder(spanExporter).build())
            .build();

        // Build OpenTelemetry instance
        openTelemetry = OpenTelemetrySdk.builder()
            .setTracerProvider(tracerProvider)
            .build();

        if (config.isDebug()) {
            System.out.println("[Pivot] Initialized with endpoint: " + config.getEndpoint());
        }
    }

    /**
     * Get OpenTelemetry instance
     */
    public static OpenTelemetry getOpenTelemetry() {
        if (openTelemetry == null) {
            throw new IllegalStateException("Pivot SDK not initialized. Call initialize() first.");
        }
        return openTelemetry;
    }

    /**
     * Get tracer instance
     */
    public static Tracer getTracer() {
        return getOpenTelemetry().getTracer(INSTRUMENTATION_NAME);
    }

    /**
     * Get current configuration
     */
    public static PivotConfig getConfig() {
        return config;
    }

    /**
     * Shutdown SDK
     */
    public static synchronized void shutdown() {
        if (openTelemetry instanceof OpenTelemetrySdk) {
            ((OpenTelemetrySdk) openTelemetry).close();
            openTelemetry = null;
            config = null;
        }
    }
}
