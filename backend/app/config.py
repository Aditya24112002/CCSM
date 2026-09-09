from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    groq_api_key: str = ""
    groq_model: str = "openai/gpt-oss-20b"
    database_url: str = "sqlite:///./backend/ccms.sqlite3"
    cors_origins: str = "http://localhost:5173"
    app_timezone: str = "Asia/Kolkata"

    model_config = SettingsConfigDict(env_file=("backend/.env", ".env"), extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
