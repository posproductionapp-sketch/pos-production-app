import pytest

from src.config.settings import Settings


def test_production_requires_database_and_long_auth_secret():
    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        Settings(environment="production", database_url="", auth_secret="x" * 32).validate_runtime()
    with pytest.raises(RuntimeError, match="AUTH_SECRET"):
        Settings(environment="production", database_url="postgresql://db/pos", auth_secret="short").validate_runtime()


def test_production_requires_postgresql():
    settings = Settings(environment="production", database_url="sqlite://", auth_secret="x" * 32)
    with pytest.raises(RuntimeError, match="PostgreSQL"):
        settings.validate_runtime()


def test_valid_production_settings_pass():
    Settings(
        environment="production",
        database_url="postgresql+psycopg://pos:secret@db/pos",
        auth_secret="x" * 32,
    ).validate_runtime()


def test_development_does_not_require_deployment_secrets():
    Settings(environment="development", database_url="", auth_secret="").validate_runtime()
