import asyncio
import json
import inspect

async def start_listener(distobject_instance):
    pubsub = distobject_instance.redis.pubsub()
    await pubsub.subscribe(distobject_instance.channel)

    async def _listen():
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue

            payload = json.loads(message["data"])
            if payload["id"] != distobject_instance.id:
                continue

            changes = payload["changes"]
            obj = distobject_instance.obj
            for field, value in changes.items():
                if hasattr(obj, field):
                    setattr(obj, field, value)

            distobject_instance._original.update(changes)

    loop = asyncio.get_running_loop()
    loop.create_task(_listen())
