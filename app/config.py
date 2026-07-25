"""Application settings, driven entirely by environment variables.

Keeping configuration in one env-driven place makes the app easy to run
identically in Docker Compose, CI, and on Render.
"""
from functools import lru_cache

from pydantic import field_validator
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

    # Default admin, seeded on startup if no user with this email exists.
    admin_email: str = "admin@shoplite.com"
    admin_password: str = "admin12345"

    # Mock payment: any card number ending with this suffix fails checkout,
    # giving the test suite a deterministic negative path.
    fail_card_suffix: str = "0000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("database_url")
    @classmethod
    def _normalize_database_url(cls, value: str) -> str:
        # Managed hosts (Render, Heroku) hand out a legacy `postgres://` URL,
        # a scheme SQLAlchemy 2.0 no longer accepts. Coerce it to the modern
        # `postgresql://` form (which uses the installed psycopg2 driver).
        if value.startswith("postgres://"):
            value = "postgresql://" + value[len("postgres://") :]
        return value

    @property
    def is_test_env(self) -> bool:
        return self.app_env == "test"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
