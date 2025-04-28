import os
import sys
import threading
import time
import pytest
import redis

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from distobject import distobject

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')

@pytest.fixture(scope="module")
def redis_client():
    client = redis.Redis(decode_responses=True, host=REDIS_HOST, port=6379, db=15)
    yield client
    client.flushdb()

class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

def test_concurrent_updates(redis_client):
    DistributedUser = distobject(redis_client)(User)

    user = DistributedUser(name="Initial", email="initial@example.com")
    user.save()
    user_id = user.get_id()

    def update_name():
        u = DistributedUser.load(user_id)
        u.name = "Thread A"
        time.sleep(0.1)
        u.save()

    def update_email():
        u = DistributedUser.load(user_id)
        u.email = "thread_b@example.com"
        time.sleep(0.1)
        u.save()

    t1 = threading.Thread(target=update_name)
    t2 = threading.Thread(target=update_email)

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    updated_user = DistributedUser.load(user_id)

    assert updated_user.name == "Thread A"
    assert updated_user.email == "thread_b@example.com"
    assert hasattr(updated_user, 'created_at')
    assert hasattr(updated_user, 'updated_at')
