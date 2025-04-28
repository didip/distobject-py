import ulid
import time
import json

def distobject(redis_client, prefix=None, channel=None):
    def decorator(cls):
        class DistributedClass(cls):
            _redis_client = redis_client
            _prefix = prefix or cls.__name__.lower()
            _channel = channel or f"{cls.__name__.lower()}-updates"

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._id = kwargs.get("id", f"{self._prefix}:{ulid.new().str}")
                self.created_at = kwargs.get("created_at", int(time.time()))
                self.updated_at = kwargs.get("updated_at", int(time.time()))

            def save(self):
                data = self.__dict__.copy()
                data.pop("_redis_client", None)
                data.pop("_prefix", None)
                data.pop("_channel", None)
                data["updated_at"] = int(time.time())
                DistributedClass._redis_client.hset(self._id, mapping=data)
                DistributedClass._redis_client.publish(self._channel, json.dumps({"id": self._id}))

            @classmethod
            def load(cls, id_):
                data = cls._redis_client.hgetall(id_)
                if not data:
                    raise ValueError(f"No object found with id {id_}")
                obj = cls(**data)
                obj._id = id_
                return obj

            def get_id(self):
                return self._id

        return DistributedClass
    return decorator
