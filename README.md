# distobject-py

![distobject](https://github.com/user-attachments/assets/34fb2c63-538f-4faf-bc18-45ad7d8d5004)

[![Build Status](https://github.com/didip/distobject-py/actions/workflows/test.yml/badge.svg)](https://github.com/didip/distobject-py/actions/workflows/test.yml)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Distributed Object Library for Python (async Redis, pure function updates, pub/sub live sync).

![distobject](https://github.com/user-attachments/assets/5c1431b6-11fe-4924-a587-788b29fff045)


---

## ✨ Features

- Async Redis backend (using `aioredis`)
- ULID-based distributed IDs
- Partial field updates (dirty tracking)
- Async listener for real-time object updates
- Pure functional updates (no in-place mutations)
- Full concurrency and stress-tested

---

## 📦 Installation

```bash
pip install -e .
```

Or if using Docker:

```bash
docker build -f Dockerfile-test -t distobject-py .
```

## 🚀 Quick Usage Example

```python
import asyncio
from distobject import DistObject
from distobject.listener import start_listener
from examples.models import User

async def main():
    redis = await DistObject.connect("redis://localhost")

    # Create and save user
    user = User(name="Alice", email="alice@example.com")
    dist = DistObject(redis, user, prefix="user", channel="user-updates")
    await dist.save()

    print(f"Saved user with ID: {dist.id}")

    # Start async listener
    await start_listener(dist)

    # Simulate a pure function update
    await asyncio.sleep(2)
    new_user = User(name="Alice", email="updated@example.com")
    dist.update(new_user)
    await dist.save()

    # Wait and observe auto-updated object
    await asyncio.sleep(5)
    print(f"Final user state: {dist.obj}")

asyncio.run(main())
```

## 🧪 Running Tests

```bash
make test

make docker-test

docker compose up --build --abort-on-container-exit --exit-code-from distobject-py-test
```