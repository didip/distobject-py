import json
import ulid
from dataclasses import asdict
import copy

class DistObject:
    def __init__(self, redis, obj, prefix="object", channel="object-updates"):
        self.redis = redis
        self.prefix = prefix
        self.channel = channel
        self.obj = obj
        self.id = None
        self._original = {}
        self._changed_fields = set()

    @staticmethod
    async def connect(redis_url):
        import aioredis
        return await aioredis.from_url(redis_url, decode_responses=True)

    def mark_changed(self, field):
        self._changed_fields.add(field)

    async def save(self):
        data = asdict(self.obj)

        if not self.id:
            self.id = f"{self.prefix}:{ulid.new().str}"
            self._changed_fields.update(data.keys())
            data["created_at"] = str(0)

        data["updated_at"] = str(0)

        mapping = {}
        for field in self._changed_fields:
            mapping[field] = str(data.get(field, ""))

        if not mapping:
            return

        await self.redis.hset(self.id, mapping)
        await self.redis.publish(self.channel, json.dumps({"id": self.id, "changes": mapping}))

        self._original.update(mapping)
        self._changed_fields.clear()

    async def load(self, key, model_cls):
        data = await self.redis.hgetall(key)
        if not data:
            raise ValueError(f"No object found with key: {key}")

        obj = model_cls(**data)
        self.obj = obj
        self.id = key
        self._original = data
        self._changed_fields = set()

        return obj

    def update(self, new_obj):
        """Pure function: diff new_obj against self.obj."""
        old = asdict(self.obj)
        new = asdict(new_obj)

        for k, v in new.items():
            if old.get(k) != v:
                self.mark_changed(k)

        self.obj = copy.deepcopy(new_obj)
