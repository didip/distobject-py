import ulid
import time
import json

def distobject(redis_client, prefix=None, channel=None):
    def decorator(cls):
        class_name = cls.__name__.lower()
        prefix_final = prefix or class_name
        channel_final = channel or f"{class_name}-updates"

        original_init = cls.__init__

        def new_init(self, *args, **kwargs):
            # Call original user-defined __init__
            original_init(self, *args, **kwargs)
            # After setting normal attributes, setup tracking
            object.__setattr__(self, '_original_data', {k: v for k, v in self.__dict__.items() if not k.startswith('_')})
            object.__setattr__(self, '_changed_fields', set())

        def new_setattr(self, name, value):
            object.__setattr__(self, name, value)
            if not name.startswith('_') and hasattr(self, '_original_data') and not getattr(self, '_suppress_tracking', False):
                old_value = self._original_data.get(name)
                if str(old_value) != str(value):
                    self._changed_fields.add(name)

        def save(self):
            if not hasattr(self, '_redis_key'):
                self._ulid = ulid.new().str
                self._redis_key = f"{self._prefix}:{self._ulid}"
                self.created_at = str(int(time.time()))
                self._changed_fields.update(["created_at"])

            self.updated_at = str(int(time.time()))
            self._changed_fields.update(["updated_at"])

            # 🔥 If nothing was changed explicitly, save everything in _original_data
            if not self._changed_fields and hasattr(self, '_original_data'):
                self._changed_fields.update(self._original_data.keys())

            if not self._changed_fields:
                return  # Nothing to save

            fields = {}
            for field in self._changed_fields:
                value = getattr(self, field, None)
                if value is not None:
                    fields[field] = str(value)

            self._redis_client.hset(self._redis_key, mapping=fields)

            notification = {
                "id": self._redis_key,
                "changes": list(fields.keys()),
            }
            self._redis_client.publish(self._channel, json.dumps(notification))

            self._original_data.update(fields)
            self._changed_fields.clear()

        @classmethod
        def load(cls, redis_key):
            data = cls._redis_client.hgetall(redis_key)
            if not data:
                raise ValueError(f"No object found at key: {redis_key}")

            obj = cls.__new__(cls)  # Create empty object

            # Suppress tracking while restoring fields
            object.__setattr__(obj, '_suppress_tracking', True)

            for k, v in data.items():
                if isinstance(v, bytes):
                    v = v.decode('utf-8')
                object.__setattr__(obj, k, v)

            object.__setattr__(obj, '_redis_key', redis_key)
            object.__setattr__(obj, '_original_data', {k: getattr(obj, k) for k in obj.__dict__ if not k.startswith('_')})
            object.__setattr__(obj, '_changed_fields', set())

            object.__delattr__(obj, '_suppress_tracking')

            return obj

        def get_id(self):
            return getattr(self, '_redis_key', None)

        # Patch the original class
        cls.__init__ = new_init
        cls.__setattr__ = new_setattr
        cls.save = save
        cls.load = load
        cls.get_id = get_id

        # Store static config into class
        cls._redis_client = redis_client
        cls._prefix = prefix_final
        cls._channel = channel_final

        return cls

    return decorator
