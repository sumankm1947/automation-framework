"""Application settings, driven entirely by environment variables.

Keeping configuration in one env-driven place makes the app easy to run
identically in Docker Compose, CI, and on Render.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Core
    app_name: str = "Shoplite"
    app_env: str = "local"  # local | test | production

    # Database
    database_url: str = "postgresql+psycopg2://shop:shop@db:5432/shop"

    # Auth (used from Milestone 2 onward)
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    # Mock payment: any card number ending with this suffix fails checkout,
    # giving the test suite a deterministic negative path.
    fail_card_suffix: str = "0000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def is_test_env(self) -> bool:
        return self.app_env == "test"


@lru_cache
def get_settings() -> Settings:
    return Settings()
