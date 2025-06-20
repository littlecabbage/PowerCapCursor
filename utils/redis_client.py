from config import get_redis_client

class RedisClient:
    """Redis客户端工具类"""
    
    @staticmethod
    def get_instance():
        return get_redis_client() 