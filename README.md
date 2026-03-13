# tiny-py

> Production-grade Python SDK for the **Tiny ERP API v2**.
> Fully typed, async-ready, and safe for FastAPI services and message queue workers.

[![PyPI version](https://img.shields.io/pypi/v/tiny-erp-py.svg)](https://pypi.org/project/tiny-erp-py/)
[![Python](https://img.shields.io/pypi/pyversions/tiny-erp-py.svg)](https://pypi.org/project/tiny-erp-py/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## Features

- **Single entry point** — all interaction through `TinyClient` or `AsyncTinyClient`
- **Typed contracts** — every method accepts and returns Pydantic v2 models
- **Automatic rate limiting** — token bucket per client instance, plan-aware (30 / 60 / 120 RPM)
- **Retry with exponential backoff** — automatic on 429 / 5xx responses
- **Sync + Async** — `TinyClient` for workers, `AsyncTinyClient` for FastAPI
- **No global state** — multiple tokens and plans can coexist in the same process

## Installation

```bash
pip install tiny-py
```

Requires Python 3.11+.

## Quick example

```python
from tiny_py import TinyClient

client = TinyClient(token="your_token", plan="advanced")

# Stream all active products
for product in client.products.iter_search():
    print(product.sku, product.name, product.price)

# Fetch a single order
order = client.orders.get("970977594")
print(order.number, order.total)
```

### Async (FastAPI)

```python
from tiny_py import AsyncTinyClient

async with AsyncTinyClient(token="your_token", plan="advanced") as client:
    products = await client.products.search()
    order = await client.orders.get("970977594")
```

## API coverage (v0.1.0)

| Resource | Methods |
|----------|---------|
| **Products** | `search`, `iter_search`, `get`, `get_stock`, `update_stock`, `update_price` |
| **Orders** | `search`, `iter_search`, `get` |

See the [roadmap](https://github.com/your-org/tiny-py) for planned resources.

## Error handling

```python
from tiny_py.exceptions import TinyAPIError, TinyRateLimitError, TinyServerError, TinyTimeoutError

try:
    order = client.orders.get(order_id)
except TinyAPIError:
    # Business error — do not retry (send to DLQ)
    ...
except (TinyRateLimitError, TinyServerError, TinyTimeoutError):
    # Transient error — re-enqueue with backoff
    ...
```

## License

MIT
