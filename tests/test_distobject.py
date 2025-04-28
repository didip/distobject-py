import asyncio
import pytest
from distobject import DistObject
from examples.models import User

@pytest.fixture
async def redis():
    r = await DistObject.connect("redis://redis:6379")
    yield r
    await r.close()

@pytest.mark.asyncio
async def test_save_new_object(redis):
    user = User(name="Alice", email="alice@example.com")
    dist = DistObject(redis, user, prefix="user", channel="user-updates")
    await dist.save()

    assert dist.id is not None

    data = await redis.hgetall(dist.id)
    assert data["name"] == "Alice"
    assert data["email"] == "alice@example.com"

@pytest.mark.asyncio
async def test_partial_update(redis):
    user = User(name="Bob", email="bob@example.com")
    dist = DistObject(redis, user, prefix="user", channel="user-updates")
    await dist.save()

    # Update email only
    new_user = User(name="Bob", email="newbob@example.com")
    dist.update(new_user)
    await dist.save()

    data = await redis.hgetall(dist.id)
    assert data["name"] == "Bob"
    assert data["email"] == "newbob@example.com"

@pytest.mark.asyncio
async def test_load_existing_object(redis):
    user = User(name="Charlie", email="charlie@example.com")
    dist = DistObject(redis, user, prefix="user", channel="user-updates")
    await dist.save()

    # Load into a fresh object
    dist2 = DistObject(redis, None, prefix="user", channel="user-updates")
    loaded_user = await dist2.load(dist.id, User)

    assert loaded_user.name == "Charlie"
    assert loaded_user.email == "charlie@example.com"

@pytest.mark.asyncio
async def test_listener_updates_object(redis):
    user = User(name="Dan", email="dan@example.com")
    dist = DistObject(redis, user, prefix="user", channel="user-updates")
    await dist.save()

    from distobject.listener import start_listener
    await start_listener(dist)

    # Simulate external update
    await asyncio.sleep(1)
    await redis.hset(dist.id, mapping={"email": "updateddan@example.com"})
    await redis.publish(dist.channel, '{"id": "' + dist.id + '", "changes": {"email": "updateddan@example.com"}}')

    await asyncio.sleep(2)

    assert dist.obj.email == "updateddan@example.com"
