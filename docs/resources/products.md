# ProductsResource

Accessed via `client.products`. Lazy-instantiated on first access.

---

## search

```python
def search(self, situacao: str = "A") -> list[Product]
```

Returns all products matching the filter. Auto-paginates through all pages.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `situacao` | `"A"` | `"A"` = active, `"I"` = inactive, `"E"` = deleted |

```python
products = client.products.search()
# or
inactive = client.products.search(situacao="I")
```

> For large catalogues, prefer `iter_search` to avoid loading everything into memory at once.

---

## iter_search

```python
def iter_search(self, situacao: str = "A") -> Iterator[Product]
```

Memory-efficient generator. Yields one `Product` at a time, fetching pages lazily.

```python
for product in client.products.iter_search():
    process(product)
```

---

## get

```python
def get(self, product_id: str) -> Product
```

Fetches full product data from `produto.obter.php`.

```python
product = client.products.get("123456")
print(product.name, product.price)
```

---

## get_stock

```python
def get_stock(self, product_id: str) -> ProductStock
```

Fetches stock per deposit from `produto.obter.estoque.php`.

```python
stock = client.products.get_stock("123456")
print(f"Total: {stock.balance} | Reserved: {stock.reserved_balance}")

for deposit in stock.deposits:
    if not deposit.ignore:
        print(f"  {deposit.name}: {deposit.balance}")
```

---

## update_stock

```python
def update_stock(self, product_id: str, request: StockUpdateRequest) -> None
```

Updates deposit balances via `produto.atualizar.estoque.php`.

```python
from tiny_py.models.product import StockUpdateRequest, StockDepositUpdate

client.products.update_stock(
    "123456",
    StockUpdateRequest(deposits=[
        StockDepositUpdate(deposit_id="1", balance=50.0),
        StockDepositUpdate(deposit_id="2", balance=20.0),
    ]),
)
```

---

## update_price

```python
def update_price(self, product_id: str, request: PriceUpdateRequest) -> None
```

Updates regular and promotional prices via `produto.atualizar.preco.php`.

```python
from tiny_py.models.product import PriceUpdateRequest

# Update regular price only
client.products.update_price("123456", PriceUpdateRequest(price=99.90))

# Update both prices
client.products.update_price("123456", PriceUpdateRequest(price=99.90, promo_price=79.90))
```

---

## Async variants

All methods are available on `AsyncTinyClient` as coroutines:

```python
async with AsyncTinyClient(token="...", plan="advanced") as client:
    products = await client.products.search()
    stock = await client.products.get_stock("123456")
```
