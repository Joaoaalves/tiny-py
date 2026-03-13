# Product Models

All models use **Pydantic v2**. Field aliases match Tiny API's Portuguese naming; English attribute names are exposed to callers.

---

## Product

Returned by `products.get()` and `products.search()`.

```python
class Product(BaseModel):
    id: str
    name: str                  # alias: "nome"
    sku: str                   # alias: "codigo"
    price: float               # alias: "preco"
    promo_price: float | None  # alias: "preco_promocional"
    cost_price: float | None   # alias: "preco_custo"
    unit: str                  # alias: "unidade"
    gtin: str | None           # alias: "gtin"
    ncm: str | None            # alias: "ncm"
    status: str                # alias: "situacao" — "A" | "I" | "E"
    category: str | None       # alias: "categoria"
    brand: str | None          # alias: "marca"
```

```python
product = client.products.get("123456")
product.name        # "Camiseta Polo"
product.sku         # "CAM-001"
product.price       # 99.90
product.promo_price # 79.90 or None
product.status      # "A"
```

---

## ProductStock

Returned by `products.get_stock()`.

```python
class ProductStock(BaseModel):
    product_id: str                # alias: "id"
    sku: str                       # alias: "codigo"
    name: str                      # alias: "nome"
    balance: float                 # alias: "saldo"
    reserved_balance: float        # alias: "saldoReservado"
    deposits: list[StockDeposit]   # alias: "depositos"
```

---

## StockDeposit

Individual deposit entry inside `ProductStock`.

```python
class StockDeposit(BaseModel):
    name: str     # alias: "nome"
    balance: float  # alias: "saldo"
    ignore: bool  # alias: "desconsiderar" — "S"/"N" coerced to bool
    company: str  # alias: "empresa"
```

> The `ignore` field is automatically coerced: `"S"` → `True`, `"N"` → `False`.

---

## StockUpdateRequest

Input model for `products.update_stock()`.

```python
class StockUpdateRequest(BaseModel):
    deposits: list[StockDepositUpdate]
```

---

## StockDepositUpdate

```python
class StockDepositUpdate(BaseModel):
    deposit_id: str  # alias: "idDeposito"
    balance: float   # alias: "saldo"
```

Example:

```python
from tiny_py.models.product import StockUpdateRequest, StockDepositUpdate

request = StockUpdateRequest(deposits=[
    StockDepositUpdate(deposit_id="1", balance=100.0),
])
```

---

## PriceUpdateRequest

Input model for `products.update_price()`.

```python
class PriceUpdateRequest(BaseModel):
    price: float
    promo_price: float | None = None
```

Example:

```python
from tiny_py.models.product import PriceUpdateRequest

request = PriceUpdateRequest(price=49.90, promo_price=39.90)
```
