from datetime import date

import pytest
from pydantic import ValidationError

from tiny_py.models.product import (
    Product,
    ProductStock,
    StockDeposit,
    StockDepositUpdate,
    StockUpdateRequest,
    PriceUpdateRequest,
)
from tiny_py.models.order import Order, OrderItem, OrderEcommerce


# ---------------------------------------------------------------------------
# StockDeposit
# ---------------------------------------------------------------------------

def test_stock_deposit_parse_ignore_s():
    d = StockDeposit.model_validate({"nome": "Dep A", "saldo": 10.0, "desconsiderar": "S", "empresa": "Loja"})
    assert d.ignore is True


def test_stock_deposit_parse_ignore_n():
    d = StockDeposit.model_validate({"nome": "Dep A", "saldo": 10.0, "desconsiderar": "N", "empresa": "Loja"})
    assert d.ignore is False


def test_stock_deposit_parse_ignore_lowercase():
    d = StockDeposit.model_validate({"nome": "Dep A", "saldo": 10.0, "desconsiderar": "s", "empresa": "Loja"})
    assert d.ignore is True


def test_stock_deposit_parse_ignore_bool_true():
    d = StockDeposit.model_validate({"nome": "Dep A", "saldo": 10.0, "desconsiderar": True, "empresa": "Loja"})
    assert d.ignore is True


def test_stock_deposit_parse_ignore_bool_false():
    d = StockDeposit.model_validate({"nome": "Dep A", "saldo": 10.0, "desconsiderar": False, "empresa": "Loja"})
    assert d.ignore is False


def test_stock_deposit_fields():
    d = StockDeposit.model_validate({"nome": "Dep B", "saldo": 5.5, "desconsiderar": "N", "empresa": "Filial"})
    assert d.name == "Dep B"
    assert d.balance == 5.5
    assert d.company == "Filial"


# ---------------------------------------------------------------------------
# ProductStock
# ---------------------------------------------------------------------------

def test_product_stock_parses_correctly():
    data = {
        "id": "123",
        "codigo": "SKU001",
        "nome": "Widget",
        "saldo": 100.0,
        "saldoReservado": 10.0,
        "depositos": [
            {"nome": "Main", "saldo": 90.0, "desconsiderar": "N", "empresa": "HQ"}
        ],
    }
    ps = ProductStock.model_validate(data)
    assert ps.product_id == "123"
    assert ps.sku == "SKU001"
    assert ps.name == "Widget"
    assert ps.balance == 100.0
    assert ps.reserved_balance == 10.0
    assert len(ps.deposits) == 1
    assert ps.deposits[0].name == "Main"


def test_product_stock_empty_deposits():
    data = {
        "id": "456",
        "codigo": "SKU002",
        "nome": "Gadget",
        "saldo": 50.0,
        "saldoReservado": 0.0,
    }
    ps = ProductStock.model_validate(data)
    assert ps.deposits == []


# ---------------------------------------------------------------------------
# Product
# ---------------------------------------------------------------------------

def test_product_all_optional_fields_none():
    data = {
        "id": "1",
        "nome": "Test Product",
        "codigo": "TP001",
        "preco": 29.99,
        "unidade": "UN",
        "situacao": "A",
    }
    p = Product.model_validate(data)
    assert p.id == "1"
    assert p.name == "Test Product"
    assert p.sku == "TP001"
    assert p.price == 29.99
    assert p.unit == "UN"
    assert p.status == "A"
    assert p.promo_price is None
    assert p.cost_price is None
    assert p.gtin is None
    assert p.ncm is None
    assert p.category is None
    assert p.brand is None


def test_product_all_fields_present():
    data = {
        "id": "2",
        "nome": "Full Product",
        "codigo": "FP001",
        "preco": 99.99,
        "preco_promocional": 79.99,
        "preco_custo": 50.00,
        "unidade": "CX",
        "gtin": "7891234567890",
        "ncm": "84713012",
        "situacao": "A",
        "categoria": "Electronics",
        "marca": "BrandX",
    }
    p = Product.model_validate(data)
    assert p.promo_price == 79.99
    assert p.cost_price == 50.00
    assert p.gtin == "7891234567890"
    assert p.ncm == "84713012"
    assert p.category == "Electronics"
    assert p.brand == "BrandX"


def test_product_price_as_string():
    """Pydantic v2 coerces string numbers to float."""
    data = {
        "id": "3",
        "nome": "Priced",
        "codigo": "PR001",
        "preco": "19.99",
        "unidade": "UN",
        "situacao": "A",
    }
    p = Product.model_validate(data)
    assert p.price == 19.99


# ---------------------------------------------------------------------------
# StockDepositUpdate
# ---------------------------------------------------------------------------

def test_stock_deposit_update_from_alias():
    d = StockDepositUpdate.model_validate({"idDeposito": "D1", "saldo": 50.0})
    assert d.deposit_id == "D1"
    assert d.balance == 50.0


def test_stock_deposit_update_from_python_name():
    d = StockDepositUpdate(deposit_id="D2", balance=25.0)
    assert d.deposit_id == "D2"


# ---------------------------------------------------------------------------
# StockUpdateRequest
# ---------------------------------------------------------------------------

def test_stock_update_request_validates():
    req = StockUpdateRequest(deposits=[
        StockDepositUpdate(deposit_id="D1", balance=10.0),
        StockDepositUpdate(deposit_id="D2", balance=20.0),
    ])
    assert len(req.deposits) == 2


# ---------------------------------------------------------------------------
# PriceUpdateRequest
# ---------------------------------------------------------------------------

def test_price_update_request_required_price():
    req = PriceUpdateRequest(price=49.99)
    assert req.price == 49.99
    assert req.promo_price is None


def test_price_update_request_with_promo():
    req = PriceUpdateRequest(price=49.99, promo_price=39.99)
    assert req.promo_price == 39.99


# ---------------------------------------------------------------------------
# OrderItem
# ---------------------------------------------------------------------------

def test_order_item_parses_from_alias():
    data = {
        "id_produto": "P001",
        "codigo": "SKU001",
        "descricao": "Widget",
        "quantidade": 2.0,
        "valor_unitario": 14.99,
    }
    item = OrderItem.model_validate(data)
    assert item.product_id == "P001"
    assert item.sku == "SKU001"
    assert item.description == "Widget"
    assert item.quantity == 2.0
    assert item.unit_price == 14.99


# ---------------------------------------------------------------------------
# OrderEcommerce
# ---------------------------------------------------------------------------

def test_order_ecommerce_parses():
    data = {
        "id": "EC001",
        "nomeEcommerce": "Mercado Livre",
        "numeroPedidoEcommerce": "MLB-123456",
    }
    ec = OrderEcommerce.model_validate(data)
    assert ec.id == "EC001"
    assert ec.name == "Mercado Livre"
    assert ec.order_number == "MLB-123456"


# ---------------------------------------------------------------------------
# Order
# ---------------------------------------------------------------------------

def test_order_date_parsing():
    data = {
        "id": "O001",
        "numero": "123",
        "data_pedido": "15/03/2024",
        "situacao": "A",
        "total_pedido": 29.99,
    }
    order = Order.model_validate(data)
    assert order.order_date == date(2024, 3, 15)


def test_order_items_default_empty():
    data = {
        "id": "O002",
        "numero": "124",
        "data_pedido": "01/01/2024",
        "situacao": "A",
        "total_pedido": 0.0,
    }
    order = Order.model_validate(data)
    assert order.items == []
    assert order.ecommerce is None
    assert order.tracking_code == ""


def test_order_with_items_and_ecommerce():
    data = {
        "id": "O003",
        "numero": "125",
        "data_pedido": "20/06/2024",
        "situacao": "F",
        "total_pedido": 59.98,
        "itens": [
            {
                "id_produto": "P001",
                "codigo": "SKU001",
                "descricao": "Widget",
                "quantidade": 2.0,
                "valor_unitario": 29.99,
            }
        ],
        "ecommerce": {
            "id": "EC001",
            "nomeEcommerce": "Shopify",
            "numeroPedidoEcommerce": "SHO-789",
        },
        "codigo_rastreamento": "BR123456789BR",
    }
    order = Order.model_validate(data)
    assert len(order.items) == 1
    assert order.items[0].product_id == "P001"
    assert order.ecommerce is not None
    assert order.ecommerce.name == "Shopify"
    assert order.tracking_code == "BR123456789BR"


def test_order_date_accepts_date_object():
    """Already a date object should pass through."""
    data = {
        "id": "O004",
        "numero": "126",
        "data_pedido": date(2024, 5, 10),
        "situacao": "A",
        "total_pedido": 10.0,
    }
    order = Order.model_validate(data)
    assert order.order_date == date(2024, 5, 10)


def test_order_invalid_date_format_raises():
    """Wrong date format should raise ValidationError."""
    data = {
        "id": "O005",
        "numero": "127",
        "data_pedido": "2024-03-15",  # wrong format (ISO instead of DD/MM/YYYY)
        "situacao": "A",
        "total_pedido": 10.0,
    }
    with pytest.raises(ValidationError):
        Order.model_validate(data)
