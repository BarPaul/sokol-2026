from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "СтудСемья"
    app_version: str = "1.0.0"
    api_prefix: str = "/api"

    database_url: str = "sqlite:///./data/semyainfo.sqlite"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    opencode_api_key: str = ""
    opencode_base_url: str = ""
    opencode_model: str = "Deepseek-v4-flash"

    ai_temperature: float = 0.2
    ai_max_tokens: int = 1024
    ai_knowledge_top_k: int = 5

    seed_admin_email: str = "admin@semyainfo.dev"
    seed_admin_password: str = "admin123"
    seed_editor_email: str = "editor@semyainfo.dev"
    seed_editor_password: str = "editor123"

    @property
    def sqlite_path(self) -> Path:
        url = self.database_url
        if url.startswith("sqlite:///"):
            p = url.removeprefix("sqlite:///")
            return Path(p)
        return Path("data/semyainfo.sqlite")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def opencode_config_ready(self) -> bool:
        return bool(self.opencode_api_key and self.opencode_base_url)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()