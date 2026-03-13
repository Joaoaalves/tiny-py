Use this skill when the user asks about the `tiny-erp-py` library or needs to write code with it.

PyPI package: `tiny-erp-py` | Python import: `tiny_py` (underscore — never `tiny_erp_py`)

## Step 1 — identify which pages to fetch

Docs base URL: `https://joaoaalves.github.io/tiny-py/`

| Topic | Path | Contains |
|-------|------|----------|
| Client setup | `client.md` | TinyClient / AsyncTinyClient constructor params, context manager, `close()` |
| Exceptions | `exceptions.md` | Full hierarchy, TinyAPIError attributes (`endpoint`, `errors`), retry table |
| Rate limiting | `rate-limiting.md` | Token bucket behaviour, multi-process coordination |
| Products API | `resources/products.md` | `search`, `iter_search`, `get`, `get_stock`, `update_stock`, `update_price` — full signatures |
| Orders API | `resources/orders.md` | `search`, `iter_search`, `get` — full signatures |
| Product models | `models/product.md` | Product, ProductStock, StockDeposit, StockDepositUpdate, StockUpdateRequest, PriceUpdateRequest |
| Order models | `models/order.md` | Order, OrderItem, OrderEcommerce — all fields and aliases |
| FastAPI | `guides/fastapi.md` | Dependency injection, lifespan, error middleware |
| Workers | `guides/rabbitmq.md` | pika / Celery patterns, DLQ routing |
| Async | `guides/async.md` | AsyncTinyClient, `asyncio.gather`, `async for`, sync vs async table |
| Install | `installation.md` | pip install, dependencies table |
| Quickstart | `quickstart.md` | 10 end-to-end usage examples |
| Roadmap | `roadmap.md` | Planned resources v0.2.0 through v0.9.0 |

Fetch **only** the page(s) that answer the question.
When the question is general or you are unsure, start with `quickstart.md`.

## Step 2 — fetch

Use the WebFetch tool with the full URL, e.g.:

```
https://joaoaalves.github.io/tiny-py/resources/products.md
```

Each URL returns raw Markdown. Use it directly to write code or explanations.

## Step 3 — answer

Write the code or explanation based solely on the fetched content.

---

## Hard rules (apply without fetching docs)

- Never `import tiny_erp_py` — always: `from tiny_py import ...`
- `orders.search(date_from, date_to)` requires `datetime.date` objects — never strings
- update_stock() and update_price() both return None
- Prefer iter_search() over search() for large datasets
- Deposits with ignore=True are excluded from totals: `sum(d.balance for d in stock.deposits if not d.ignore)`
- TinyAPIError must NOT be retried — send to DLQ; only TinyRateLimitError, TinyServerError, TinyTimeoutError should requeue
- TinyClient does not accept session or any transport object
- timeout is always a tuple[float, float] — never a single float
- Unit tests must mock HTTPAdapter, never requests.Session directly
