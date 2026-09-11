from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    backend_host: str = "127.0.0.1"
    backend_port: int = 8000

    llama_host: str = "127.0.0.1"
    llama_port: int = 8080

    gateway_host: str = "127.0.0.1"
    gateway_port: int = 8081

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60


settings = Settings()
