import redis
import os
import traceback
from redis.exceptions import RedisError


class RedisConnection:
    def __init__(self):
        try:
            password = os.getenv('REDISPASSWORD')
            if not (password and password.strip()):
                self.client = redis.Redis(
                    host=os.getenv('REDISHOST', "localhost"),
                    port=os.getenv('REDISPORT', 6379),
                    decode_responses=True)
            else:
                self.client = redis.Redis(
                    host=os.getenv('REDISHOST', "localhost"),
                    port=os.getenv('REDISPORT', 6379),
                    password=password,
                    decode_responses=True)
            self.client.ping()
        except RedisError as e:
            traceback.print_exc()
            raise Exception('Redis unavailable')

    def get_connection(self):
        return self.client


if __name__ == "__main__":
    redis_conn = RedisConnection()
    conn = redis_conn.get_connection()
