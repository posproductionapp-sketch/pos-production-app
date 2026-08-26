"""Small Redis boundary used by queue/cache infrastructure.

The application talks to Redis only through this module so the vendor dependency
remains isolated from domain logic.
"""

from redis import Redis


def create_redis_client(redis_url: str) -> Redis:
    if not redis_url:
        raise RuntimeError("REDIS_URL is required")
    return Redis.from_url(redis_url, decode_responses=True, health_check_interval=30)


def check_redis(client: Redis) -> bool:
    return bool(client.ping())
