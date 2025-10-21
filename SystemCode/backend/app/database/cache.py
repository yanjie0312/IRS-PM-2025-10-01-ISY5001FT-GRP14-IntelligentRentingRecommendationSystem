import os
import redis
from functools import lru_cache


@lru_cache() 
def get_redis_client() -> redis.Redis:
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    pool = redis.ConnectionPool(host=redis_host, port=redis_port, db=0, decode_responses=True)
    return redis.Redis(connection_pool=pool)


def get_redis() -> redis.Redis:
    return get_redis_client()