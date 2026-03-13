# FastAPI Integration

Use `AsyncTinyClient` in FastAPI to avoid blocking the event loop.

## Dependency setup

```python
# deps.py
from functools import lru_cache
from tiny_py import AsyncTinyClient

@lru_cache(maxsize=1)
def _client() -> AsyncTinyClient:
    return AsyncTinyClient(token=settings.TINY_TOKEN, plan=settings.TINY_PLAN)

async def get_tiny() -> AsyncTinyClient:
    return _client()
```

`lru_cache` ensures a single client instance per process — one shared HTTP connection pool and one rate limiter.

---

## Route examples

```python
# router.py
from fastapi import APIRouter, Depends
from tiny_py import AsyncTinyClient
from tiny_py.exceptions import TinyAPIError

from .deps import get_tiny

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/{product_id}/stock")
async def get_stock(
    product_id: str,
    client: AsyncTinyClient = Depends(get_tiny),
):
    return await client.products.get_stock(product_id)

@router.get("/{product_id}")
async def get_product(
    product_id: str,
    client: AsyncTinyClient = Depends(get_tiny),
):
    return await client.products.get(product_id)
```

---

## Error handling middleware

Map tiny-py exceptions to HTTP responses:

```python
# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from tiny_py.exceptions import TinyAPIError, TinyAuthError, TinyRateLimitError

app = FastAPI()

@app.exception_handler(TinyAuthError)
async def auth_error_handler(request: Request, exc: TinyAuthError):
    return JSONResponse(status_code=401, content={"detail": "Tiny API auth failed"})

@app.exception_handler(TinyAPIError)
async def api_error_handler(request: Request, exc: TinyAPIError):
    return JSONResponse(status_code=422, content={"detail": str(exc), "errors": exc.errors})

@app.exception_handler(TinyRateLimitError)
async def rate_limit_handler(request: Request, exc: TinyRateLimitError):
    return JSONResponse(status_code=503, content={"detail": "Upstream rate limit"})
```

---

## Application lifespan

Close the client cleanly on shutdown:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from .deps import _client

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await _client().close()

app = FastAPI(lifespan=lifespan)
```

---

## Settings example

```python
# settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TINY_TOKEN: str
    TINY_PLAN: str = "advanced"

settings = Settings()
```
