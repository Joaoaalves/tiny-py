# TinyClient

## TinyClient

Synchronous client. Wraps `requests.Session` — safe for threads and message queue workers.

### Constructor

```python
TinyClient(
    token: str,
    plan: Literal["free", "basic", "advanced"] = "advanced",
    timeout: tuple[float, float] = (5.0, 30.0),
    max_retries: int = 3,
    base_url: str = "https://api.tiny.com.br/api2",
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `token` | `str` | — | Tiny API token |
| `plan` | `str` | `"advanced"` | Controls built-in RPM limit |
| `timeout` | `tuple` | `(5.0, 30.0)` | `(connect_timeout, read_timeout)` in seconds |
| `max_retries` | `int` | `3` | Max retry attempts on 429 / 5xx |
| `base_url` | `str` | Tiny API v2 URL | Override for tests or proxies |

> `TinyClient` does **not** accept a `session`, `httpx.Client`, or any transport object — transport is an internal concern.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `products` | `ProductsResource` | Lazy-instantiated products resource |
| `orders` | `OrdersResource` | Lazy-instantiated orders resource |

### Methods

```python
client.close() -> None
```

Closes the underlying HTTP session. Called automatically when used as a context manager.

### Context manager

```python
with TinyClient(token="...", plan="advanced") as client:
    products = client.products.search()
```

---

## AsyncTinyClient

Async client. Uses `httpx.AsyncClient` internally — safe for FastAPI and async event loops.

### Constructor

Same parameters as `TinyClient`.

### Properties

Same as `TinyClient`, but resources return async variants.

### Async context manager

```python
async with AsyncTinyClient(token="...", plan="advanced") as client:
    products = await client.products.search()
    order = await client.orders.get("970977594")
```

> Use `AsyncTinyClient` in FastAPI to avoid blocking the event loop.

---

## Multiple clients in the same process

Each client instance has its own rate limiter and HTTP session — they never share state:

```python
client_a = TinyClient(token="token_a", plan="basic")
client_b = TinyClient(token="token_b", plan="advanced")

# Independent rate limiters — safe
products_a = client_a.products.search()
products_b = client_b.products.search()
```
