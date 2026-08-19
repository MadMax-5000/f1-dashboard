from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PostgresDsn, RedisDsn, SecretStr
from typing import Literal
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    log_level: str = "DEBUG"

    project_name: str = "F1 Digital Twin"
    version: str = "0.1.0"
    api_prefix: str = "/api/v1"

    db_url: PostgresDsn = Field(
        default="postgresql+asyncpg://f1twin:f1twin_dev@localhost:5432/f1twin",
        alias="DB_URL",
    )
    db_pool_size: int = 20
    db_max_overflow: int = 10
    db_echo: bool = False

    redis_url: RedisDsn = Field(
        default="redis://localhost:6379/0",
        alias="REDIS_URL",
    )

    kafka_bootstrap_servers: str = Field(
        default="localhost:9092",
        alias="KAFKA_BOOTSTRAP_SERVERS",
    )
    kafka_race_events_topic: str = "race.events"
    kafka_telemetry_topic: str = "race.telemetry"
    kafka_simulation_topic: str = "twin.simulation"

    minio_endpoint: str = Field(default="localhost:9000", alias="MINIO_ENDPOINT")
    minio_access_key: str = Field(default="f1twin", alias="MINIO_ACCESS_KEY")
    minio_secret_key: SecretStr = Field(default="f1twin_dev", alias="MINIO_SECRET_KEY")
    minio_bucket_raw: str = "f1-raw"
    minio_bucket_processed: str = "f1-processed"
    minio_bucket_models: str = "f1-models"
    minio_bucket_video: str = "f1-video"
    minio_bucket_simulations: str = "f1-simulations"

    neo4j_uri: str = Field(default="bolt://localhost:7687", alias="NEO4J_URI")
    neo4j_user: str = Field(default="neo4j", alias="NEO4J_USER")
    neo4j_password: SecretStr = Field(default="f1twin_dev", alias="NEO4J_PASSWORD")

    milvus_host: str = Field(default="localhost", alias="MILVUS_HOST")
    milvus_port: int = 19530

    data_dir: Path = Field(default=Path("/data"), alias="DATA_DIR")
    raw_data_dir: Path = Field(default=Path("/data/raw"), alias="RAW_DATA_DIR")
    processed_data_dir: Path = Field(default=Path("/data/processed"), alias="PROCESSED_DATA_DIR")

    cv_model_dir: Path = Field(default=Path("/data/models/cv"), alias="CV_MODEL_DIR")
    ml_model_dir: Path = Field(default=Path("/data/models/ml"), alias="ML_MODEL_DIR")

    ray_head_address: str = Field(default="ray://localhost:10001")
    ray_num_cpus: int = 8
    ray_num_gpus: int = 0

    celery_broker_url: str = Field(default="redis://localhost:6379/0")
    celery_result_backend: str = Field(default="redis://localhost:6379/0")

    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    auth_secret_key: SecretStr = Field(default="dev-secret-change-in-prod")
    auth_token_expire_minutes: int = 1440

    sentry_dsn: str | None = None

    mlflow_tracking_uri: str = Field(default="http://localhost:5000", alias="MLFLOW_TRACKING_URI")
    wandb_project: str = "f1-digital-twin"
    wandb_entity: str | None = None

    @property
    def db_url_sync(self) -> str:
        return str(self.db_url).replace("+asyncpg", "")

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


settings = Settings()
