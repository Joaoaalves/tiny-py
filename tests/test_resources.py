import json
from collections.abc import Iterator
from datetime import date
from unittest.mock import MagicMock, call

import pytest

from tiny_py.resources._base import BaseResource
from tiny_py.resources.products import ProductsResource
from tiny_py.resources.orders import OrdersResource
from tiny_py.models.product import (
    Product,
    ProductStock,
    StockUpdateRequest,
    StockDepositUpdate,
    PriceUpdateRequest,
)
from tiny_py.models.order import Order, OrderItem


# ---------------------------------------------------------------------------
# Fake HTTPAdapter helpers
# ---------------------------------------------------------------------------

class FakeHTTPAdapter:
    """Fake HTTPAdapter that returns pre-configured responses."""

    def __init__(self):
        self.get_calls: list[tuple] = []
        self.post_calls: list[tuple] = []
        self._get_responses: list[dict] = []
        self._post_responses: list[dict] = []

    def queue_get(self, response: dict) -> None:
        self._get_responses.append(response)

    def queue_post(self, response: dict) -> None:
        self._post_responses.append(response)

    def get(self, endpoint: str, params: dict | None = None) -> dict:
        self.get_calls.append((endpoint, params or {}))
        return self._get_responses.pop(0)

    def post(self, endpoint: str, data: dict | None = None) -> dict:
        self.post_calls.append((endpoint, data or {}))
        return self._post_responses.pop(0)


def make_product_dict(**overrides) -> dict:
    base = {
        "id": "1",
        "nome": "Test Product",
        "codigo": "TP001",
        "preco": 29.99,
        "unidade": "UN",
        "situacao": "A",
    }
    base.update(overrides)
    return base


def make_order_dict(**overrides) -> dict:
    base = {
        "id": "O001",
        "numero": "123",
        "data_pedido": "15/03/2024",
        "situacao": "A",
        "total_pedido": 99.99,
    }
    base.update(overrides)
    return base


def make_product_stock_dict(**overrides) -> dict:
    base = {
        "id": "1",
        "codigo": "TP001",
        "nome": "Test Product",
        "saldo": 100.0,
        "saldoReservado": 5.0,
        "depositos": [],
    }
    base.update(overrides)
    return base


def single_page_produtos(products: list[dict]) -> dict:
    return {
        "status": "OK",
        "numero_paginas": 1,
        "produtos": [{"produto": p} for p in products],
    }


def multi_page_produtos(products: list[dict], page: int, total_pages: int) -> dict:
    return {
        "status": "OK",
        "numero_paginas": total_pages,
        "produtos": [{"produto": p} for p in products],
    }


def single_page_pedidos(orders: list[dict]) -> dict:
    return {
        "status": "OK",
        "numero_paginas": 1,
        "pedidos": [{"pedido": o} for o in orders],
    }


# ---------------------------------------------------------------------------
# BaseResource._paginate
# ---------------------------------------------------------------------------

def test_paginate_single_page():
    http = FakeHTTPAdapter()
    http.queue_get(single_page_produtos([make_product_dict(id="1"), make_product_dict(id="2")]))
    resource = BaseResource(http)
    items = list(resource._paginate("produto.pesquisa.php", "produtos", "produto", {}))
    assert len(items) == 2
    assert items[0]["id"] == "1"
    assert items[1]["id"] == "2"


def test_paginate_multiple_pages():
    http = FakeHTTPAdapter()
    http.queue_get(multi_page_produtos([make_product_dict(id="1")], page=1, total_pages=2))
    http.queue_get(multi_page_produtos([make_product_dict(id="2")], page=2, total_pages=2))
    resource = BaseResource(http)
    items = list(resource._paginate("produto.pesquisa.php", "produtos", "produto", {}))
    assert len(items) == 2
    assert items[0]["id"] == "1"
    assert items[1]["id"] == "2"


def test_paginate_stops_at_last_page():
    http = FakeHTTPAdapter()
    http.queue_get({
        "status": "OK",
        "numero_paginas": 1,
        "produtos": [],
    })
    resource = BaseResource(http)
    items = list(resource._paginate("produto.pesquisa.php", "produtos", "produto", {}))
    assert items == []
    assert len(http.get_calls) == 1


def test_paginate_passes_page_param():
    http = FakeHTTPAdapter()
    http.queue_get(single_page_produtos([]))
    resource = BaseResource(http)
    list(resource._paginate("produto.pesquisa.php", "produtos", "produto", {"situacao": "A"}))
    _, params = http.get_calls[0]
    assert params["pagina"] == 1
    assert params["situacao"] == "A"


def test_paginate_three_pages():
    http = FakeHTTPAdapter()
    for i in range(1, 4):
        http.queue_get(multi_page_produtos([make_product_dict(id=str(i))], page=i, total_pages=3))
    resource = BaseResource(http)
    items = list(resource._paginate("produto.pesquisa.php", "produtos", "produto", {}))
    assert len(items) == 3
    assert len(http.get_calls) == 3


# ---------------------------------------------------------------------------
# ProductsResource.search
# ---------------------------------------------------------------------------

def test_products_search_returns_list():
    http = FakeHTTPAdapter()
    http.queue_get(single_page_produtos([make_product_dict(id="1"), make_product_dict(id="2")]))
    resource = ProductsResource(http)
    products = resource.search()
    assert isinstance(products, list)
    assert len(products) == 2
    assert all(isinstance(p, Product) for p in products)


def test_products_search_with_situacao():
    http = FakeHTTPAdapter()
    http.queue_get(single_page_produtos([]))
    resource = ProductsResource(http)
    resource.search(situacao="I")
    _, params = http.get_calls[0]
    assert params["situacao"] == "I"


# ---------------------------------------------------------------------------
# ProductsResource.iter_search
# ---------------------------------------------------------------------------

def test_products_iter_search_is_generator():
    http = FakeHTTPAdapter()
    http.queue_get(single_page_produtos([make_product_dict(id="1")]))
    resource = ProductsResource(http)
    gen = resource.iter_search()
    assert isinstance(gen, Iterator)
    products = list(gen)
    assert len(products) == 1
    assert isinstance(products[0], Product)


# ---------------------------------------------------------------------------
# ProductsResource.get
# ---------------------------------------------------------------------------

def test_products_get_returns_product():
    http = FakeHTTPAdapter()
    http.queue_get({"status": "OK", "produto": make_product_dict(id="42")})
    resource = ProductsResource(http)
    product = resource.get("42")
    assert isinstance(product, Product)
    assert product.id == "42"


def test_products_get_calls_correct_endpoint():
    http = FakeHTTPAdapter()
    http.queue_get({"status": "OK", "produto": make_product_dict(id="99")})
    resource = ProductsResource(http)
    resource.get("99")
    endpoint, params = http.get_calls[0]
    assert endpoint == "produto.obter.php"
    assert params["id"] == "99"


# ---------------------------------------------------------------------------
# ProductsResource.get_stock
# ---------------------------------------------------------------------------

def test_products_get_stock_returns_product_stock():
    http = FakeHTTPAdapter()
    http.queue_get({"status": "OK", "produto": make_product_stock_dict(id="5")})
    resource = ProductsResource(http)
    stock = resource.get_stock("5")
    assert isinstance(stock, ProductStock)
    assert stock.product_id == "5"


def test_products_get_stock_calls_correct_endpoint():
    http = FakeHTTPAdapter()
    http.queue_get({"status": "OK", "produto": make_product_stock_dict()})
    resource = ProductsResource(http)
    resource.get_stock("5")
    endpoint, params = http.get_calls[0]
    assert endpoint == "produto.obter.estoque.php"
    assert params["id"] == "5"


# ---------------------------------------------------------------------------
# ProductsResource.update_stock
# ---------------------------------------------------------------------------

def test_products_update_stock_calls_post():
    http = FakeHTTPAdapter()
    http.queue_post({"status": "OK"})
    resource = ProductsResource(http)
    req = StockUpdateRequest(deposits=[
        StockDepositUpdate(deposit_id="D1", balance=50.0),
    ])
    resource.update_stock("10", req)
    assert len(http.post_calls) == 1
    endpoint, data = http.post_calls[0]
    assert endpoint == "produto.atualizar.estoque.php"
    assert data["id"] == "10"
    deposits = json.loads(data["depositos"])
    assert deposits[0]["idDeposito"] == "D1"
    assert deposits[0]["saldo"] == 50.0


def test_products_update_stock_multiple_deposits():
    http = FakeHTTPAdapter()
    http.queue_post({"status": "OK"})
    resource = ProductsResource(http)
    req = StockUpdateRequest(deposits=[
        StockDepositUpdate(deposit_id="D1", balance=10.0),
        StockDepositUpdate(deposit_id="D2", balance=20.0),
    ])
    resource.update_stock("10", req)
    _, data = http.post_calls[0]
    deposits = json.loads(data["depositos"])
    assert len(deposits) == 2


# ---------------------------------------------------------------------------
# ProductsResource.update_price
# ---------------------------------------------------------------------------

def test_products_update_price_calls_post():
    http = FakeHTTPAdapter()
    http.queue_post({"status": "OK"})
    resource = ProductsResource(http)
    req = PriceUpdateRequest(price=49.99)
    resource.update_price("10", req)
    endpoint, data = http.post_calls[0]
    assert endpoint == "produto.atualizar.preco.php"
    assert data["id"] == "10"
    assert data["preco"] == 49.99
    assert "preco_promocional" not in data


def test_products_update_price_with_promo():
    http = FakeHTTPAdapter()
    http.queue_post({"status": "OK"})
    resource = ProductsResource(http)
    req = PriceUpdateRequest(price=49.99, promo_price=39.99)
    resource.update_price("10", req)
    _, data = http.post_calls[0]
    assert data["preco_promocional"] == 39.99


# ---------------------------------------------------------------------------
# OrdersResource.search
# ---------------------------------------------------------------------------

def test_orders_search_returns_list():
    http = FakeHTTPAdapter()
    http.queue_get(single_page_pedidos([make_order_dict(id="O1"), make_order_dict(id="O2")]))
    resource = OrdersResource(http)
    orders = resource.search(date(2024, 1, 1), date(2024, 1, 31))
    assert isinstance(orders, list)
    assert len(orders) == 2
    assert all(isinstance(o, Order) for o in orders)


def test_orders_search_passes_date_params():
    http = FakeHTTPAdapter()
    http.queue_get(single_page_pedidos([]))
    resource = OrdersResource(http)
    resource.search(date(2024, 3, 1), date(2024, 3, 31))
    _, params = http.get_calls[0]
    assert params["dataInicial"] == "01/03/2024"
    assert params["dataFinal"] == "31/03/2024"


# ---------------------------------------------------------------------------
# OrdersResource.iter_search
# ---------------------------------------------------------------------------

def test_orders_iter_search_is_generator():
    http = FakeHTTPAdapter()
    http.queue_get(single_page_pedidos([make_order_dict(id="O1")]))
    resource = OrdersResource(http)
    gen = resource.iter_search(date(2024, 1, 1), date(2024, 1, 31))
    assert isinstance(gen, Iterator)
    orders = list(gen)
    assert len(orders) == 1
    assert isinstance(orders[0], Order)


# ---------------------------------------------------------------------------
# OrdersResource.get
# ---------------------------------------------------------------------------

def test_orders_get_returns_order():
    http = FakeHTTPAdapter()
    http.queue_get({"status": "OK", "pedido": make_order_dict(id="O99")})
    resource = OrdersResource(http)
    order = resource.get("O99")
    assert isinstance(order, Order)
    assert order.id == "O99"


def test_orders_get_calls_correct_endpoint():
    http = FakeHTTPAdapter()
    http.queue_get({"status": "OK", "pedido": make_order_dict()})
    resource = OrdersResource(http)
    resource.get("O50")
    endpoint, params = http.get_calls[0]
    assert endpoint == "pedido.obter.php"
    assert params["id"] == "O50"


# ---------------------------------------------------------------------------
# Pagination: multiple pages for orders
# ---------------------------------------------------------------------------

def test_orders_search_multiple_pages():
    http = FakeHTTPAdapter()
    http.queue_get({
        "status": "OK",
        "numero_paginas": 2,
        "pedidos": [{"pedido": make_order_dict(id="O1")}],
    })
    http.queue_get({
        "status": "OK",
        "numero_paginas": 2,
        "pedidos": [{"pedido": make_order_dict(id="O2")}],
    })
    resource = OrdersResource(http)
    orders = resource.search(date(2024, 1, 1), date(2024, 1, 31))
    assert len(orders) == 2
    assert orders[0].id == "O1"
    assert orders[1].id == "O2"
    assert len(http.get_calls) == 2
