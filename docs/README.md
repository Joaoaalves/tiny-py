# tiny-py

> Production-grade Python SDK for the **Tiny ERP API v2**.
> Fully typed, async-ready, and safe for FastAPI services and message queue workers.

---

## Features

- **Single entry point** — all interaction through `TinyClient` or `AsyncTinyClient`
- **Typed contracts** — every method accepts and returns Pydantic v2 models
- **Automatic rate limiting** — token bucket per client instance, plan-aware
- **Retry with backoff** — exponential backoff on 429 / 5xx responses
- **Sync + Async** — `TinyClient` for workers, `AsyncTinyClient` for FastAPI
- **No global state** — multiple tokens/plans can coexist in the same process

## Quick example

```python
from tiny_py import TinyClient

client = TinyClient(token="your_token", plan="advanced")

# List all active products
for product in client.products.iter_search():
    print(product.sku, product.name, product.price)

# Fetch a single order
order = client.orders.get("970977594")
print(order.number, order.total)
```

## Requirements

- Python **3.11+**
- `requests`, `httpx`, `pydantic>=2`

## Targets

This library targets **Tiny ERP API v2** (`https://api.tiny.com.br/api2`).
API v3 uses OAuth 2.0 and a different resource structure — do not mix calls.
