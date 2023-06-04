# noinspection PyUnresolvedReferences
import redis

database = redis.Redis(host="localhost", port=6379, db=0)
