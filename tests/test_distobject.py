import os
import sys
import pytest
import redis
import re

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

def test_save_load_user(redis_client):
    DistributedUser = distobject(redis_client)(User)

    user = DistributedUser(name="Alice", email="alice@example.com")
    user.save()

    # --- Check object fields after save() ---

    # Basic fields
    assert user.get_id() is not None
    assert redis_client.exists(user.get_id())

    # Internal fields
    assert hasattr(user, '_original_data')
    assert hasattr(user, '_changed_fields')
    assert hasattr(user, '_redis_key')

    # _original_data must contain key fields
    for key in ["name", "email", "created_at", "updated_at"]:
        assert key in user._original_data

    # Field types
    assert isinstance(user._original_data["name"], str)
    assert isinstance(user._original_data["email"], str)
    assert re.match(r"^\d+$", user._original_data["created_at"])
    assert re.match(r"^\d+$", user._original_data["updated_at"])

    # Dirty tracking
    assert isinstance(user._changed_fields, set)
    assert len(user._changed_fields) == 0  # No dirty fields after save

    # Redis key structure
    assert user.get_id().startswith("user:")

    # --- Load object back ---

    loaded_user = DistributedUser.load(user.get_id())

    # Internal fields
    assert hasattr(loaded_user, '_original_data')
    assert hasattr(loaded_user, '_changed_fields')
    assert hasattr(loaded_user, '_redis_key')

    # _original_data must contain key fields
    for key in ["name", "email", "created_at", "updated_at"]:
        assert key in loaded_user._original_data

    # Field types
    assert isinstance(loaded_user._original_data["name"], str)
    assert isinstance(loaded_user._original_data["email"], str)
    assert re.match(r"^\d+$", loaded_user._original_data["created_at"])
    assert re.match(r"^\d+$", loaded_user._original_data["updated_at"])

    # Dirty tracking
    assert isinstance(loaded_user._changed_fields, set)
    assert len(loaded_user._changed_fields) == 0  # No dirty fields after load

    # Redis key structure
    assert loaded_user.get_id().startswith("user:")

    # Field values
    assert loaded_user.name == "Alice"
    assert loaded_user.email == "alice@example.com"
