# OrdersResource

Accessed via `client.orders`. Lazy-instantiated on first access.

---

## search

```python
def search(self, date_from: date, date_to: date) -> list[Order]
```

Returns all orders in the given date range. Auto-paginates through all pages.

```python
from datetime import date

orders = client.orders.search(
    date_from=date(2024, 1, 1),
    date_to=date(2024, 1, 31),
)
```

> For large date ranges, prefer `iter_search` to avoid loading all orders into memory.

---

## iter_search

```python
def iter_search(self, date_from: date, date_to: date) -> Iterator[Order]
```

Memory-efficient generator. Yields one `Order` at a time, fetching pages lazily.

```python
from datetime import date

for order in client.orders.iter_search(date(2024, 1, 1), date(2024, 1, 31)):
    process(order)
```

---

## get

```python
def get(self, order_id: str) -> Order
```

Fetches full order details from `pedido.obter.php`.

```python
order = client.orders.get("970977594")
print(order.number, order.status, order.total)

for item in order.items:
    print(item.sku, item.quantity, item.unit_price)

if order.ecommerce:
    print(order.ecommerce.order_number)
```

---

## Async variants

```python
async with AsyncTinyClient(token="...", plan="advanced") as client:
    orders = await client.orders.search(date(2024, 1, 1), date(2024, 1, 31))
    order = await client.orders.get("970977594")
```
