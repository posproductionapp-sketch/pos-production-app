"""Environment-driven application configuration.

Secrets are loaded from environment/deployment secret storage only.
"""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import os


@dataclass(frozen=True)
class Settings:
    environment: str
    database_url: str
    auth_secret: str
    redis_url: str = ""
    openai_api_key: str | None = None
    allowed_hosts: tuple[str, ...] = ()
    max_request_body_bytes: int = 2 * 1024 * 1024
    vat_rate: Decimal = Decimal("0")

    def validate_runtime(self) -> None:
        """Fail closed for production while keeping local/unit test boot lightweight."""
        if self.max_request_body_bytes < 1:
            raise RuntimeError("MAX_REQUEST_BODY_BYTES must be positive")
        if self.vat_rate < 0 or self.vat_rate > 1:
            raise RuntimeError("VAT_RATE must be between 0 and 1")
        if self.environment == "production":
            if not self.database_url:
                raise RuntimeError("DATABASE_URL is required")
            if not self.redis_url:
                raise RuntimeError("REDIS_URL is required")
            if len(self.auth_secret) < 32:
                raise RuntimeError("AUTH_SECRET must be at least 32 characters")
            if not self.database_url.startswith(("postgresql://", "postgresql+psycopg://")):
                raise RuntimeError("Production DATABASE_URL must use PostgreSQL")
            if not self.redis_url.startswith(("redis://", "rediss://")):
                raise RuntimeError("Production REDIS_URL must use Redis")
            if not self.allowed_hosts:
                raise RuntimeError("ALLOWED_HOSTS is required in production")
            if "*" in self.allowed_hosts:
                raise RuntimeError("ALLOWED_HOSTS must not contain wildcard '*' in production")


def _decimal_env(name: str, default: str) -> Decimal:
    try:
        value = Decimal(os.getenv(name, default))
    except InvalidOperation as exc:
        raise RuntimeError(f"{name} must be a decimal") from exc
    if value < 0 or value > 1:
        raise RuntimeError(f"{name} must be between 0 and 1")
    return value


def load_settings() -> Settings:
    environment = os.getenv("APP_ENV", "development").strip().lower()
    database_url = os.getenv("DATABASE_URL", "").strip()
    auth_secret = os.getenv("AUTH_SECRET", "")
    redis_url = os.getenv("REDIS_URL", "").strip()
    raw_hosts = os.getenv("ALLOWED_HOSTS", "").strip()
    allowed_hosts = tuple(host.strip() for host in raw_hosts.split(",") if host.strip())
    try:
        max_request_body_bytes = int(os.getenv("MAX_REQUEST_BODY_BYTES", str(2 * 1024 * 1024)))
    except ValueError as exc:
        raise RuntimeError("MAX_REQUEST_BODY_BYTES must be an integer") from exc
    return Settings(
        environment=environment,
        database_url=database_url,
        auth_secret=auth_secret,
        redis_url=redis_url,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        allowed_hosts=allowed_hosts,
        max_request_body_bytes=max_request_body_bytes,
        vat_rate=_decimal_env("VAT_RATE", "0"),
    )
