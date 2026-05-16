# Pivot Java SDK

Java SDK for the Pivot AI Agent Reliability Platform.

## Installation

### Maven

```xml
<dependency>
    <groupId>ai.pivot</groupId>
    <artifactId>pivot-sdk-java</artifactId>
    <version>0.1.0</version>
</dependency>
```

### Gradle

```gradle
implementation 'ai.pivot:pivot-sdk-java:0.1.0'
```

## Quick Start

```java
import ai.pivot.core.PivotSDK;
import ai.pivot.core.PivotConfig;
import ai.pivot.openai.OpenAIInstrumentation;

// Initialize Pivot SDK
PivotConfig config = PivotConfig.builder()
    .endpoint("http://localhost:4317")
    .serviceName("my-agent")
    .debug(true)
    .build();

PivotSDK.initialize(config);

// Instrument OpenAI
OpenAIInstrumentation.instrument();

// Your agent code runs normally - traces are automatically captured
// ... OpenAI API calls ...

// Shutdown when done
PivotSDK.shutdown();
```

## Features

- **Auto-instrumentation** for OpenAI Java SDK
- **OpenTelemetry integration** with OTLP export
- **harness.* attributes** for agent-specific metadata
- **Thread-safe** context propagation
- **Spring Boot** auto-configuration support

## Spring Boot Integration

Add `@EnablePivot` to your Spring Boot application:

```java
@SpringBootApplication
@EnablePivot
public class MyAgentApplication {
    public static void main(String[] args) {
        SpringApplication.run(MyAgentApplication.class, args);
    }
}
```

Configure in `application.properties`:

```properties
pivot.endpoint=http://localhost:4317
pivot.service-name=my-agent
pivot.debug=true
```

## License

Apache 2.0
