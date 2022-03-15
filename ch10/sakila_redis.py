import os
import json

import redis
import pymysql


class DB:
    def __init__(self, **params):
        params.setdefault("charset", "utf8mb4")
        params.setdefault("cursorclass", pymysql.cursors.DictCursor)

        self.mysql = pymysql.connect(**params)

    def query(self, sql):
        with self.mysql.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def store(self, sql, values):
        with self.mysql.cursor() as cursor:
            cursor.execute(sql, values)
            return cursor.fetchone()


# Time to live for cached data
TTL = 10

# Obtain the Redis details
REDIS_URL = os.environ.get('REDIS_URL')

# Obtain the DB credentials
DB_HOST = os.environ.get('DB_HOST')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')
DB_NAME = os.environ.get('DB_NAME')

# Create a database variable
Database = DB(host=DB_HOST, user=DB_USER, password=DB_PASS, db=DB_NAME)

# Create a Redis variable
Cache = redis.Redis.from_url(REDIS_URL)


def scan(sql):
    """Retrieve records from the cache, or else from the database."""
    res = Cache.get(sql)

    if res:
        print("Retrieved from cache")
        return json.loads(res)
        
        
    res = Database.query(sql)
    Cache.setex(sql, TTL, json.dumps(res))
    return res


def retrieve(id):
    """Retrieve a record from the cache, or else from the database."""
    key = f"actor:{id}"
    res = Cache.hgetall(key)

    if res:
        print("Retrieved from cache")
        return res

    sql = "SELECT `first_name`, `last_name` FROM `actor` WHERE `actor_id`=%s"
    res = Database.store(sql, (id,))

    if res:
        Cache.hmset(key, res)
        Cache.expire(key, TTL)

    return res


# Display the result of some queries
print(scan("SELECT first_name, last_name FROM actor"))
print(retrieve(1))
print(retrieve(2))
print(retrieve(3))
