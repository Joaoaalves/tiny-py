from collections.abc import Iterator
from datetime import date

from tiny_py._http import HTTPAdapter
from tiny_py.models.order import Order
from tiny_py.resources._base import BaseResource


class OrdersResource(BaseResource):
    def search(self, date_from: date, date_to: date) -> list[Order]:
        """Returns all orders in the date range (auto-paginated)."""
        return list(self.iter_search(date_from=date_from, date_to=date_to))

    def iter_search(self, date_from: date, date_to: date) -> Iterator[Order]:
        """Memory-efficient generator."""
        params = {
            "dataInicial": date_from.strftime("%d/%m/%Y"),
            "dataFinal": date_to.strftime("%d/%m/%Y"),
        }
        for item in self._paginate(
            endpoint="pedido.pesquisa.php",
            collection_key="pedidos",
            item_key="pedido",
            params=params,
        ):
            yield Order.model_validate(item)

    def get(self, order_id: str) -> Order:
        """Fetches full order details (pedido.obter.php)."""
        retorno = self._http.get("pedido.obter.php", {"id": order_id})
        return Order.model_validate(retorno["pedido"])
