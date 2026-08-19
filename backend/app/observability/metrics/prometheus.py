from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Summary,
    Info,
    generate_latest,
    REGISTRY,
)
from prometheus_client.multiprocess import MultiProcessCollector
import structlog
import time
from functools import wraps
from typing import Any, Callable

logger = structlog.get_logger()

# ── API Metrics ──
HTTP_REQUESTS_TOTAL = Counter(
    "f1_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)
HTTP_REQUEST_DURATION = Histogram(
    "f1_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)
HTTP_IN_FLIGHT = Gauge("f1_http_in_flight", "Current HTTP requests in flight", ["method"])

# ── Race Metrics ──
RACES_RECONSTRUCTED = Counter("f1_races_reconstructed_total", "Total races reconstructed")
RACE_RECONSTRUCTION_DURATION = Histogram(
    "f1_race_reconstruction_duration_seconds",
    "Race reconstruction duration",
    buckets=(1, 5, 10, 30, 60, 120, 300),
)
LAPS_PROCESSED = Counter("f1_laps_processed_total", "Total laps processed", ["session_type"])
TELEMETRY_FRAMES_INGESTED = Counter(
    "f1_telemetry_frames_ingested_total", "Total telemetry frames ingested", ["source"]
)

# ── Simulation Metrics ──
SIMULATIONS_RUN = Counter("f1_simulations_run_total", "Total simulation runs", ["type"])
SIMULATION_DURATION = Histogram(
    "f1_simulation_duration_seconds",
    "Simulation duration",
    buckets=(0.1, 0.5, 1, 5, 10, 30, 60, 120),
)
SIMULATION_TICKS = Counter("f1_simulation_ticks_total", "Total simulation ticks processed")
ACTIVE_SIMULATIONS = Gauge("f1_active_simulations", "Currently active simulations")

# ── ML Metrics ──
ML_PREDICTIONS = Counter("f1_ml_predictions_total", "Total ML predictions", ["model", "type"])
ML_PREDICTION_LATENCY = Histogram(
    "f1_ml_prediction_latency_seconds",
    "ML prediction latency",
    ["model"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
)
MODEL_INFERENCE_ERRORS = Counter(
    "f1_model_inference_errors_total", "Model inference errors", ["model", "error_type"]
)

# ── Data Pipeline Metrics ──
DATA_PIPELINE_EVENTS = Counter(
    "f1_data_pipeline_events_total", "Data pipeline events", ["pipeline", "status"]
)
DATA_PIPELINE_DURATION = Histogram(
    "f1_data_pipeline_duration_seconds",
    "Data pipeline stage duration",
    ["pipeline", "stage"],
)
KAFKA_MESSAGES_PRODUCED = Counter(
    "f1_kafka_messages_produced_total", "Kafka messages produced", ["topic"]
)
KAFKA_MESSAGES_CONSUMED = Counter(
    "f1_kafka_messages_consumed_total", "Kafka messages consumed", ["topic"]
)

# ── Cache Metrics ──
CACHE_HITS = Counter("f1_cache_hits_total", "Cache hits", ["tier"])
CACHE_MISSES = Counter("f1_cache_misses_total", "Cache misses", ["tier"])
CACHE_SIZE = Gauge("f1_cache_size_bytes", "Cache size in bytes", ["tier"])

# ── Resource Metrics ──
GPU_UTILIZATION = Gauge("f1_gpu_utilization_percent", "GPU utilization", ["device"])
GPU_MEMORY_USED = Gauge("f1_gpu_memory_used_bytes", "GPU memory used", ["device"])
RAY_TASKS_PENDING = Gauge("f1_ray_tasks_pending", "Ray tasks pending")
RAY_TASKS_RUNNING = Gauge("f1_ray_tasks_running", "Ray tasks running")
QUEUE_SIZE = Gauge("f1_queue_size", "Task queue size", ["queue"])

# ── Business Metrics ──
CURRENT_RACE_LAP = Gauge("f1_current_race_lap", "Current race lap number", ["session_id"])
DRIVERS_ACTIVE = Gauge("f1_drivers_active", "Number of active drivers in session", ["session_id"])
PIT_STOPS_TOTAL = Counter("f1_pit_stops_total", "Total pit stops", ["session_id"])
OVERTAKES_TOTAL = Counter("f1_overtakes_total", "Total overtakes detected", ["session_id"])
STRATEGY_RECOMMENDATIONS = Counter(
    "f1_strategy_recommendations_total", "Strategy recommendations generated", ["type"]
)

# ── Info ──
APP_INFO = Info("f1_app", "Application information")
APP_INFO.info({"version": "0.1.0", "name": "f1-digital-twin"})


def track_duration(metric: Histogram | Counter, **labels):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.monotonic()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.monotonic() - start
                if isinstance(metric, Histogram):
                    metric.labels(**labels).observe(duration)
                elif isinstance(metric, Counter):
                    metric.labels(**labels).inc(duration)

        return wrapper

    return decorator


def track_http(method: str, endpoint: str):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            HTTP_IN_FLIGHT.labels(method=method).inc()
            start = time.monotonic()
            try:
                result = await func(*args, **kwargs)
                HTTP_REQUESTS_TOTAL.labels(method=method, endpoint=endpoint, status="200").inc()
                return result
            except Exception as e:
                HTTP_REQUESTS_TOTAL.labels(method=method, endpoint=endpoint, status="500").inc()
                raise
            finally:
                HTTP_IN_FLIGHT.labels(method=method).dec()
                HTTP_REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(
                    time.monotonic() - start
                )

        return wrapper

    return decorator
