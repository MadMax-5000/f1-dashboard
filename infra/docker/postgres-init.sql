CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE SCHEMA IF NOT EXISTS f1;

-- Enable TimescaleDB for telemetry tables
SELECT create_hypertable('telemetry_frames', 'timestamp', if_not_exists => TRUE);
SELECT create_hypertable('car_data', 'timestamp', if_not_exists => TRUE);
SELECT create_hypertable('weather_records', 'timestamp', if_not_exists => TRUE);
