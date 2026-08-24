"""Environment-driven application configuration.

No credentials or API keys belong in source control.
"""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    environment: str
    openai_api_key: str | None = None


def load_settings() -> Settings:
    environment = os.getenv("APP_ENV", "development")
    api_key = os.getenv("OPENAI_API_KEY")
    return Settings(environment=environment, openai_api_key=api_key)
