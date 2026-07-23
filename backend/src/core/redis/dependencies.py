from .main import RedisService, redis_service


def get_redis_service() -> RedisService:
    return redis_service
