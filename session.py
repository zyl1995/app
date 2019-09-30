import redis
import hashlib
import time

pool = redis.ConnectionPool(host='localhost', port=6379)
redis_connection = redis.Redis(connection_pool=pool)

SESSION_EXPIRE = 600


class RedisSession:

    def __init__(self, session_id):
        if session_id and redis_connection.exists(session_id):
            self.session_id = session_id
        else:
            self.session_id = self._generate_random_str()
            redis_connection.hset(self.session_id, '', '')
            redis_connection.expire(self.session_id, SESSION_EXPIRE)

    def _generate_random_str(self):
        md5_obj = hashlib.md5()
        md5_obj.update(bytes(str(time.time()), encoding='utf-8'))
        return md5_obj.hexdigest()

    def __setitem__(self, key, value):
        redis_connection.hset(self.session_id, key, value)
        redis_connection.expire(self.session_id, SESSION_EXPIRE)

    def __getitem__(self, item):
        return redis_connection.hget(self.session_id, item)

    def __delitem__(self, key):
        redis_connection.hdel(self.session_id, key)
        redis_connection.expire(self.session_id, SESSION_EXPIRE)
