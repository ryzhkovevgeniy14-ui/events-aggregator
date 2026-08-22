from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_connection_string: str
    postgres_database_name: str
    postgres_host: str
    postgres_port: int
    postgres_username: str
    postgres_password: str
    events_provider_base_url: str
    events_provider_api_key: str

    model_config = SettingsConfigDict(
        extra="ignore",
    )


settings = Settings()