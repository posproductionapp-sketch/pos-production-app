"""Environment-driven application configuration.

Secrets are loaded from environment/deployment secret storage only.
"""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    environment: str
    database_url: str
    auth_secret: str
    openai_api_key: str | None = None

    def validate_runtime(self) -> None:
        """Fail closed for production while keeping local/unit test boot lightweight."""
        if self.environment == "production":
            if not self.database_url:
                raise RuntimeError("DATABASE_URL is required")
            if len(self.auth_secret) < 32:
                raise RuntimeError("AUTH_SECRET must be at least 32 characters")
            if not self.database_url.startswith(("postgresql://", "postgresql+psycopg://")):
                raise RuntimeError("Production DATABASE_URL must use PostgreSQL")
        elif self.database_url and len(self.auth_secret) < 32:
            raise RuntimeError("AUTH_SECRET must be at least 32 characters when configured")


def load_settings() -> Settings:
    environment = os.getenv("APP_ENV", "development").strip().lower()
    database_url = os.getenv("DATABASE_URL", "").strip()
    auth_secret = os.getenv("AUTH_SECRET", "")
    return Settings(
        environment=environment,
        database_url=database_url,
        auth_secret=auth_secret,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )
