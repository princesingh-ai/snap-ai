from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    backend_host: str = "127.0.0.1"
    backend_port: int = 8000

    llama_host: str = "127.0.0.1"
    llama_port: int = 8080

    gateway_host: str = "127.0.0.1"
    gateway_port: int = 8081

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
