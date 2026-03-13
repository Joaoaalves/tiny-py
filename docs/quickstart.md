# Quickstart

## 1. Instantiate the client

```python
from tiny_py import TinyClient

client = TinyClient(
    token="your_token",
    plan="advanced",       # "free" | "basic" | "advanced"
    timeout=(5.0, 30.0),   # (connect_timeout, read_timeout)
    max_retries=3,
)
```

Plan controls the built-in rate limiter:

| Plan | Requests/min |
|------|-------------|
| `free` | 30 |
| `basic` | 60 |
| `advanced` | 120 |

---

## 2. List products

```python
# Materialise the full list (convenient for small catalogues)
products = client.products.search()

# Memory-efficient generator (preferred for large catalogues)
for product in client.products.iter_search():
    print(product.sku, product.name, product.price)
```

Filter by status:

```python
# "A" = active (default), "I" = inactive, "E" = deleted
inactive = client.products.search(situacao="I")
```

---

## 3. Fetch a single product

```python
product = client.products.get("123456")
print(product.id, product.name, product.price)
```

---

## 4. Check stock

```python
stock = client.products.get_stock("123456")
print(stock.balance)

for deposit in stock.deposits:
    print(deposit.name, deposit.balance)
```

---

## 5. Update stock

```python
from tiny_py.models.product import StockUpdateRequest, StockDepositUpdate

client.products.update_stock(
    "123456",
    StockUpdateRequest(deposits=[
        StockDepositUpdate(deposit_id="1", balance=100.0),
    ]),
)
```

---

## 6. Update price

```python
from tiny_py.models.product import PriceUpdateRequest

client.products.update_price(
    "123456",
    PriceUpdateRequest(price=49.90, promo_price=39.90),
)
```

---

## 7. Search orders

```python
from datetime import date

orders = client.orders.search(
    date_from=date(2024, 1, 1),
    date_to=date(2024, 1, 31),
)

for order in orders:
    print(order.number, order.order_date, order.total)
```

---

## 8. Fetch a single order

```python
order = client.orders.get("970977594")
print(order.number, order.status, order.total)

for item in order.items:
    print(item.sku, item.quantity, item.unit_price)
```

---

## 9. Use as a context manager

```python
with TinyClient(token="your_token", plan="advanced") as client:
    products = client.products.search()
# Session is closed automatically
```

---

## 10. Error handling

```python
from tiny_py.exceptions import TinyAPIError, TinyRateLimitError, TinyServerError, TinyTimeoutError

try:
    order = client.orders.get("invalid_id")
except TinyAPIError as exc:
    # Business error — do not retry
    print("API error:", exc, exc.errors)
except (TinyRateLimitError, TinyServerError, TinyTimeoutError) as exc:
    # Transient error — safe to re-enqueue with backoff
    print("Transient error:", exc)
```
