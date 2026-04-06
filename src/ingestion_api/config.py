from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TPP Smartwatch Ingestion API"
    api_prefix: str = "/api/v1"
    model_artifact_path: str = "models/trained_model.pkl"
    jwt_secret_key: str = Field(default="change-this-in-production", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    database_url: str = Field(
        default="sqlite:///./data/ingestion.db",
        alias="DATABASE_URL",
    )

    default_alignment_seconds: int = 60

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
