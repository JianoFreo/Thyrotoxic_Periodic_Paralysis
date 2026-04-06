from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TPP Smartwatch Ingestion API"
    api_prefix: str = "/api/v1"

    # TimescaleDB (PostgreSQL) is recommended for production time-series workloads.
    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/tpp",
        alias="DATABASE_URL",
    )

    # Fallback alignment when client does not provide a sampling interval.
    default_alignment_seconds: int = 60

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
