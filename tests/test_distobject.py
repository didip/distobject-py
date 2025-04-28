import pytest
import redis
from distobject import distobject

@pytest.fixture(scope="module")
def redis_client():
    client = redis.Redis(decode_responses=True, host="localhost", port=6379, db=15)
    yield client
    client.flushdb()

@distobject(redis_client=redis_client)
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

def test_save_load_user(redis_client):
    user = User(name="Alice", email="alice@example.com")
    user.save()

    assert user.get_id() is not None
    assert redis_client.exists(user.get_id())

    loaded_user = User.load(user.get_id())

    assert loaded_user.name == "Alice"
    assert loaded_user.email == "alice@example.com"
    assert hasattr(loaded_user, 'created_at')
    assert hasattr(loaded_user, 'updated_at')
    assert int(loaded_user.created_at) <= int(loaded_user.updated_at)

def test_load_non_existent(redis_client):
    with pytest.raises(ValueError):
        User.load("nonexistent_key")
