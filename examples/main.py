import asyncio
from distobject import DistObject
from distobject.listener import start_listener
from examples.models import User

async def main():
    redis = await DistObject.connect("redis://redis:6379")

    user = User(name="Alice", email="alice@example.com")
    dist = DistObject(redis, user, prefix="user", channel="user-updates")
    await dist.save()

    print(f"Saved user: {dist.id}")

    await start_listener(dist)

    # Simulate local update
    await asyncio.sleep(2)
    new_user = User(name="Alice", email="updated@example.com")
    dist.update(new_user)
    await dist.save()

    await asyncio.sleep(5)
    print(f"Final user state: {dist.obj}")

asyncio.run(main())
