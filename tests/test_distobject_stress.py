import os
import sys
import threading
import time
import pytest
import redis

# Fix: Add project root to sys.path
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

def test_stress_concurrent_updates(redis_client):
    # Decorate the User class dynamically
    DistributedUser = distobject(redis_client)(User)

    user = DistributedUser(name="Base", email="base@example.com")
    user.save()
    user_id = user.get_id()

    results = []
    lock = threading.Lock()

    def worker(index):
        try:
            u = DistributedUser.load(user_id)
            u.name = f"User {index}"
            u.email = f"user{index}@example.com"
            time.sleep(0.01)
            u.save()
            with lock:
                results.append(f"Success-{index}")
        except Exception as e:
            with lock:
                results.append(f"Fail-{index}-{str(e)}")

    threads = []
    for i in range(100):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    final_user = DistributedUser.load(user_id)

    print(f"Final user.name: {final_user.name}")
    print(f"Final user.email: {final_user.email}")

    assert final_user.name.startswith("User ")
    assert final_user.email.startswith("user") and final_user.email.endswith("@example.com")
    assert len(results) == 100
    assert all(r.startswith("Success-") for r in results)
