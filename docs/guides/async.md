# Async Usage

`AsyncTinyClient` mirrors `TinyClient` exactly, using `httpx.AsyncClient` and `AsyncRateLimiter` internally.

## Basic usage

```python
import asyncio
from tiny_py import AsyncTinyClient

async def main():
    async with AsyncTinyClient(token="your_token", plan="advanced") as client:
        products = await client.products.search()
        order = await client.orders.get("970977594")

asyncio.run(main())
```

---

## Concurrent requests

Use `asyncio.gather` to fetch multiple resources concurrently. The rate limiter is still enforced — requests are serialised through `AsyncRateLimiter.acquire()`:

```python
async def fetch_multiple(client: AsyncTinyClient, product_ids: list[str]):
    tasks = [client.products.get(pid) for pid in product_ids]
    return await asyncio.gather(*tasks)
```

---

## Async generator

```python
async def stream_products(client: AsyncTinyClient):
    async for product in client.products.iter_search():
        await save_to_db(product)
```

---

## Resource methods

All `TinyClient` methods exist on `AsyncTinyClient` as `async def` coroutines:

| Sync | Async |
|------|-------|
| `client.products.search()` | `await client.products.search()` |
| `client.products.iter_search()` | `async for p in client.products.iter_search()` |
| `client.products.get(id)` | `await client.products.get(id)` |
| `client.products.get_stock(id)` | `await client.products.get_stock(id)` |
| `client.products.update_stock(id, req)` | `await client.products.update_stock(id, req)` |
| `client.products.update_price(id, req)` | `await client.products.update_price(id, req)` |
| `client.orders.search(from, to)` | `await client.orders.search(from, to)` |
| `client.orders.iter_search(from, to)` | `async for o in client.orders.iter_search(from, to)` |
| `client.orders.get(id)` | `await client.orders.get(id)` |

---

## When to use sync vs async

| Scenario | Client |
|----------|--------|
| FastAPI endpoint | `AsyncTinyClient` |
| asyncio script | `AsyncTinyClient` |
| Celery task | `TinyClient` |
| pika / RabbitMQ worker | `TinyClient` |
| CLI script | `TinyClient` |
| Jupyter notebook | Either (async with `await` in cells) |

---

## Lifecycle

Prefer the async context manager to ensure the underlying `httpx.AsyncClient` is properly closed:

```python
async with AsyncTinyClient(token="...", plan="advanced") as client:
    ...
# httpx session closed here
```

Or close manually:

```python
client = AsyncTinyClient(token="...", plan="advanced")
try:
    ...
finally:
    await client.close()
```
