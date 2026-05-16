-- Pivot ClickHouse Schema
-- Optimized for high-throughput span ingestion and fast queries

-- Main spans table
CREATE TABLE IF NOT EXISTS spans (
    -- Trace identifiers
    trace_id UUID,
    span_id UUID,
    parent_span_id Nullable(UUID),

    -- Span metadata
    name LowCardinality(String),
    kind Enum8('INTERNAL'=1, 'CLIENT'=2, 'SERVER'=3, 'PRODUCER'=4, 'CONSUMER'=5),
    start_time DateTime64(9),
    end_time DateTime64(9),
    duration_ns UInt64,
    status_code Enum8('UNSET'=0, 'OK'=1, 'ERROR'=2),

    -- OTel GenAI core attributes
    gen_ai_operation_name LowCardinality(String),
    gen_ai_request_model LowCardinality(String),
    gen_ai_provider_name LowCardinality(String),
    gen_ai_usage_input_tokens UInt32,
    gen_ai_usage_output_tokens UInt32,

    -- Pivot harness extensions
    harness_run_id String,
    harness_checkpoint_id Nullable(String),
    harness_policy_version String,
    harness_policy_decision Enum8('allow'=1, 'deny'=2, 'ask'=3, 'rewrite'=4, 'budget_exhausted'=5),
    harness_policy_rail_name LowCardinality(String),
    harness_stakeholder_principal LowCardinality(String),
    harness_stakeholder_principal_type Enum8('owner'=1, 'user'=2, 'agent'=3, 'tool'=4, 'external'=5),
    harness_replay_hash String,
    harness_provenance_model_fingerprint String,
    harness_provenance_seed Nullable(Int32),
    harness_provenance_temperature Nullable(Float32),

    -- Full attributes as Map for flexibility
    attributes Map(String, String),

    -- Resource attributes
    resource_attributes Map(String, String),

    -- Events (for exceptions, logs)
    events Nested(
        timestamp DateTime64(9),
        name String,
        attributes Map(String, String)
    ),

    -- Indexes for fast queries
    INDEX idx_run_id harness_run_id TYPE bloom_filter GRANULARITY 1,
    INDEX idx_trace_id trace_id TYPE bloom_filter GRANULARITY 1,
    INDEX idx_model gen_ai_request_model TYPE set(0) GRANULARITY 1,
    INDEX idx_principal harness_stakeholder_principal TYPE set(0) GRANULARITY 1

) ENGINE = MergeTree()
PARTITION BY toYYYYMM(start_time)
ORDER BY (start_time, trace_id, span_id)
SETTINGS index_granularity = 8192;

-- Materialized view for hourly metrics
CREATE MATERIALIZED VIEW IF NOT EXISTS span_metrics_hourly
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMMDD(hour)
ORDER BY (hour, gen_ai_request_model, harness_policy_decision)
AS SELECT
    toStartOfHour(start_time) AS hour,
    gen_ai_request_model,
    gen_ai_provider_name,
    harness_policy_decision,
    harness_stakeholder_principal_type,
    count() AS span_count,
    sum(gen_ai_usage_input_tokens) AS total_input_tokens,
    sum(gen_ai_usage_output_tokens) AS total_output_tokens,
    avg(duration_ns) AS avg_duration_ns,
    quantile(0.50)(duration_ns) AS p50_duration_ns,
    quantile(0.95)(duration_ns) AS p95_duration_ns,
    quantile(0.99)(duration_ns) AS p99_duration_ns
FROM spans
GROUP BY hour, gen_ai_request_model, gen_ai_provider_name,
         harness_policy_decision, harness_stakeholder_principal_type;

-- Materialized view for run-level aggregates
CREATE MATERIALIZED VIEW IF NOT EXISTS run_metrics
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMMDD(start_time)
ORDER BY (harness_run_id, start_time)
AS SELECT
    harness_run_id,
    min(start_time) AS start_time,
    max(end_time) AS end_time,
    count() AS total_spans,
    sum(gen_ai_usage_input_tokens) AS total_input_tokens,
    sum(gen_ai_usage_output_tokens) AS total_output_tokens,
    countIf(harness_policy_decision = 'deny') AS denied_spans,
    countIf(status_code = 'ERROR') AS error_spans,
    uniq(trace_id) AS unique_traces
FROM spans
GROUP BY harness_run_id;

-- Materialized view for policy decisions
CREATE MATERIALIZED VIEW IF NOT EXISTS policy_decisions_hourly
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMMDD(hour)
ORDER BY (hour, harness_policy_rail_name, harness_policy_decision)
AS SELECT
    toStartOfHour(start_time) AS hour,
    harness_policy_rail_name,
    harness_policy_decision,
    harness_stakeholder_principal_type,
    count() AS decision_count
FROM spans
WHERE harness_policy_rail_name != ''
GROUP BY hour, harness_policy_rail_name, harness_policy_decision,
         harness_stakeholder_principal_type;

-- Table for evaluation results
CREATE TABLE IF NOT EXISTS eval_results (
    id UUID,
    task_id String,
    run_id String,
    sample_id String,
    timestamp DateTime64(9),

    -- Scores
    score Float32,
    scorer_type LowCardinality(String),
    scorer_name LowCardinality(String),

    -- Metadata
    model LowCardinality(String),
    epoch UInt8,
    success Boolean,

    -- Full result as JSON
    result_json String,

    INDEX idx_task_id task_id TYPE bloom_filter GRANULARITY 1,
    INDEX idx_run_id run_id TYPE bloom_filter GRANULARITY 1

) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (timestamp, task_id, run_id)
SETTINGS index_granularity = 8192;

-- Table for replay checkpoints
CREATE TABLE IF NOT EXISTS replay_checkpoints (
    checkpoint_id String,
    run_id String,
    step_number UInt32,
    timestamp DateTime64(9),

    -- State snapshot
    state_json String,

    -- Provenance
    determinism_hash String,

    INDEX idx_run_id run_id TYPE bloom_filter GRANULARITY 1

) ENGINE = MergeTree()
ORDER BY (run_id, step_number)
SETTINGS index_granularity = 8192;
