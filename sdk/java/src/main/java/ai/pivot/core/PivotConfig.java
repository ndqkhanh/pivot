package ai.pivot.core;

import java.util.HashMap;
import java.util.Map;

/**
 * Configuration for Pivot SDK
 */
public class PivotConfig {
    private final String endpoint;
    private final String serviceName;
    private final boolean debug;
    private final Map<String, String> attributes;

    private PivotConfig(Builder builder) {
        this.endpoint = builder.endpoint;
        this.serviceName = builder.serviceName;
        this.debug = builder.debug;
        this.attributes = new HashMap<>(builder.attributes);
    }

    public String getEndpoint() {
        return endpoint;
    }

    public String getServiceName() {
        return serviceName;
    }

    public boolean isDebug() {
        return debug;
    }

    public Map<String, String> getAttributes() {
        return new HashMap<>(attributes);
    }

    public static Builder builder() {
        return new Builder();
    }

    public static class Builder {
        private String endpoint = "http://localhost:4317";
        private String serviceName = "pivot-agent";
        private boolean debug = false;
        private Map<String, String> attributes = new HashMap<>();

        public Builder endpoint(String endpoint) {
            this.endpoint = endpoint;
            return this;
        }

        public Builder serviceName(String serviceName) {
            this.serviceName = serviceName;
            return this;
        }

        public Builder debug(boolean debug) {
            this.debug = debug;
            return this;
        }

        public Builder attribute(String key, String value) {
            this.attributes.put(key, value);
            return this;
        }

        public Builder attributes(Map<String, String> attributes) {
            this.attributes.putAll(attributes);
            return this;
        }

        public PivotConfig build() {
            return new PivotConfig(this);
        }
    }
}
