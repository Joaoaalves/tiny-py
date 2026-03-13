# Order Models

---

## Order

Returned by `orders.get()` and `orders.search()`.

```python
class Order(BaseModel):
    id: str
    number: str                         # alias: "numero"
    order_date: date                    # alias: "data_pedido" — parsed from "DD/MM/YYYY"
    status: str                         # alias: "situacao"
    items: list[OrderItem]              # alias: "itens" — defaults to []
    ecommerce: OrderEcommerce | None    # alias: "ecommerce" — None if not an e-commerce order
    total: float                        # alias: "total_pedido"
    tracking_code: str                  # alias: "codigo_rastreamento" — defaults to ""
```

```python
order = client.orders.get("970977594")
order.number        # "123"
order.order_date    # date(2024, 1, 15)
order.total         # 199.80
order.tracking_code # "BR123456789XX" or ""
```

> `order_date` is automatically parsed from Tiny's `"DD/MM/YYYY"` format into a Python `date` object.

---

## OrderItem

Individual line item inside an `Order`.

```python
class OrderItem(BaseModel):
    product_id: str   # alias: "id_produto"
    sku: str          # alias: "codigo"
    description: str  # alias: "descricao"
    quantity: float   # alias: "quantidade"
    unit_price: float # alias: "valor_unitario"
```

```python
for item in order.items:
    total = item.quantity * item.unit_price
    print(f"{item.sku}: {item.quantity} × {item.unit_price} = {total:.2f}")
```

---

## OrderEcommerce

Present when the order originated from an e-commerce integration.

```python
class OrderEcommerce(BaseModel):
    id: str
    name: str          # alias: "nomeEcommerce"
    order_number: str  # alias: "numeroPedidoEcommerce"
```

```python
if order.ecommerce:
    print(order.ecommerce.name)          # "Shopify"
    print(order.ecommerce.order_number)  # "1001"
```
