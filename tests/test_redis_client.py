import pytest

from src.infrastructure.redis.client import create_redis_client


def test_redis_client_requires_url():
    with pytest.raises(RuntimeError, match="REDIS_URL is required"):
        create_redis_client("")


def test_redis_client_uses_configured_url():
    client = create_redis_client("redis://localhost:6379/7")
    assert client.connection_pool.connection_kwargs["host"] == "localhost"
    assert client.connection_pool.connection_kwargs["db"] == 7
