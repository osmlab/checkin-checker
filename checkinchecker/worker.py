import os
import redis
from rq import Worker, Queue, Connection
from checkinchecker.util import setup_loghandlers


listen = ['high', 'default', 'low']
redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
conn = redis.from_url(redis_url)

if __name__ == '__main__':
    setup_loghandlers()
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work(burst=True)
