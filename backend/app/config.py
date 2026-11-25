from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = f"sqlite:///{Path(__file__).resolve().parent.parent / 'freightproof.db'}"
    supabase_url: str | None = None
    supabase_key: str | None = None
    cors_origins: str = "http://localhost:5178,http://127.0.0.1:5178"
    api_port: int = 8006

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()