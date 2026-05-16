# Pivot Gateway

Production-grade Go service for receiving OTLP traces and enforcing policies.

## Features

- **OTLP Receiver**: gRPC and HTTP endpoints for OpenTelemetry traces
- **Policy Enforcement**: OPA-based guardrails with <30ms p99 latency
- **ClickHouse Writer**: High-performance span storage
- **Health Checks**: Readiness and liveness endpoints

## Quick Start

```bash
# Build
go build -o pivot-gateway ./cmd/gateway

# Run
./pivot-gateway

# Or with Docker
docker build -t pivot-gateway .
docker run -p 4317:4317 -p 4318:4318 pivot-gateway
```

## Configuration

Environment variables:

```bash
PIVOT_GRPC_PORT=4317          # gRPC port
PIVOT_HTTP_PORT=4318          # HTTP port
CLICKHOUSE_URL=http://localhost:8123
POLICY_ENGINE_URL=http://localhost:8181
ENABLE_POLICY=true            # Enable policy enforcement
```

## Architecture

```
OTLP Spans → Gateway → Policy Engine → ClickHouse
                ↓
            Redis (live state)
```

## Development

```bash
# Install dependencies
go mod download

# Run tests
go test ./...

# Run with hot reload
air
```

## Performance

- **Throughput**: 50k spans/s per node
- **Latency**: <30ms p99 for fast rails
- **Memory**: ~200MB baseline

## License

Apache 2.0
