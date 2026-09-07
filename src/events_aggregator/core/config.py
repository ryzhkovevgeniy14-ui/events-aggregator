from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения, загружаемые из переменных окружения."""
    postgres_connection_string: str
    postgres_database_name: str
    postgres_host: str
    postgres_port: int
    postgres_username: str
    postgres_password: str
    events_provider_base_url: str
    events_provider_api_key: str
    capashino_base_url: str
    capashino_api_key: str
    glitchtip_dsn: str

    outbox_interval: int = 5
    outbox_batch_size: int = 100
    idempotency_retention_days: int = 30

    model_config = SettingsConfigDict(
        extra="ignore",
    )


settings = Settings()