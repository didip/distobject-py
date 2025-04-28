import asyncio
import pytest
from distobject import DistObject
from examples.models import User
from distobject.listener import start_listener

@pytest.fixture
async def redis():
    r = await DistObject.connect("redis://redis:6379")
    yield r
    await r.close()

@pytest.mark.asyncio
async def test_concurrent_updates(redis):
    user = User(name="Concurrent", email="concurrent@example.com")
    dist = DistObject(redis, user, prefix="user", channel="user-updates")
    await dist.save()

    await start_listener(dist)

    async def update_name(index):
        await asyncio.sleep(0.1)
        updated_user = User(name=f"User-{index}", email=user.email)
        dist.update(updated_user)
        await dist.save()

    async def update_email(index):
        await asyncio.sleep(0.1)
        updated_user = User(name=user.name, email=f"user{index}@example.com")
        dist.update(updated_user)
        await dist.save()

    tasks = []
    for i in range(10):
        tasks.append(update_name(i))
        tasks.append(update_email(i))

    await asyncio.gather(*tasks)

    await asyncio.sleep(2)

    # After all updates, the object should have some final name and email
    assert dist.obj.name.startswith("User-")
    assert dist.obj.email.startswith("user")

@pytest.mark.asyncio
async def test_stress_save_load(redis):
    tasks = []

    async def save_and_load(index):
        user = User(name=f"StressUser-{index}", email=f"stress{index}@example.com")
        dist = DistObject(redis, user, prefix="user", channel="user-updates")
        await dist.save()

        dist2 = DistObject(redis, None, prefix="user", channel="user-updates")
        loaded_user = await dist2.load(dist.id, User)

        assert loaded_user.name == f"StressUser-{index}"
        assert loaded_user.email == f"stress{index}@example.com"

    for i in range(50):  # Stress 50 objects concurrently
        tasks.append(save_and_load(i))

    await asyncio.gather(*tasks)
