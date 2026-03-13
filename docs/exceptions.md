# Exceptions

All exceptions inherit from `TinyError`, so callers can catch broadly or narrowly.

## Hierarchy

```
TinyError
├── TinyAPIError          ← status != "OK" from Tiny API
│   └── TinyAuthError     ← invalid/expired token
├── TinyRateLimitError    ← HTTP 429, retries exhausted
├── TinyServerError       ← HTTP 5xx, retries exhausted
└── TinyTimeoutError      ← request timed out, retries exhausted
```

---

## TinyError

```python
class TinyError(Exception):
    """Base for all tiny-py errors."""
```

Catch this to handle any error from the library.

---

## TinyAPIError

```python
class TinyAPIError(TinyError):
    def __init__(self, message: str, endpoint: str, errors: list[str]) -> None: ...

    message: str        # first error message
    endpoint: str       # API endpoint that failed
    errors: list[str]   # all error strings from the response
```

Raised when the Tiny API responds with `status != "OK"` — a **business-level** error.

> **Do not retry** — re-sending the same request will produce the same error.
> Send to a Dead Letter Queue or log for manual inspection.

```python
try:
    order = client.orders.get("invalid_id")
except TinyAPIError as exc:
    print(exc.endpoint)  # "pedido.obter.php"
    print(exc.errors)    # ["Pedido não encontrado"]
```

---

## TinyAuthError

```python
class TinyAuthError(TinyAPIError): ...
```

Subclass of `TinyAPIError`. Raised when the token is invalid or expired.

```python
from tiny_py.exceptions import TinyAuthError

try:
    client.products.search()
except TinyAuthError:
    # Rotate the token and restart the worker
    ...
```

---

## TinyRateLimitError

```python
class TinyRateLimitError(TinyError): ...
```

HTTP 429 received after all retry attempts are exhausted. The built-in rate limiter prevents most 429s from reaching this point — this only surfaces when the server-side limit is tighter than expected.

---

## TinyServerError

```python
class TinyServerError(TinyError): ...
```

HTTP 5xx after all retry attempts with exponential backoff. Indicates a transient server-side issue.

---

## TinyTimeoutError

```python
class TinyTimeoutError(TinyError): ...
```

The request timed out after all retry attempts. Adjust `timeout` on the client if you're hitting this on large responses.

---

## Retry guidance

| Exception | Retry? | Action |
|-----------|--------|--------|
| `TinyAPIError` | No | Send to DLQ |
| `TinyAuthError` | No | Rotate token |
| `TinyRateLimitError` | Yes | Re-enqueue with backoff |
| `TinyServerError` | Yes | Re-enqueue with backoff |
| `TinyTimeoutError` | Yes | Re-enqueue with backoff |
