from collections.abc import AsyncIterator
from datetime import date

from tiny_py.models.order import Order
from tiny_py.resources._async_base import AsyncBaseResource


class AsyncOrdersResource(AsyncBaseResource):
    async def search(self, date_from: date, date_to: date) -> list[Order]:
        """Returns all orders in the date range (auto-paginated)."""
        return [o async for o in self.iter_search(date_from=date_from, date_to=date_to)]

    async def iter_search(self, date_from: date, date_to: date) -> AsyncIterator[Order]:
        """Memory-efficient async generator."""
        params = {
            "dataInicial": date_from.strftime("%d/%m/%Y"),
            "dataFinal": date_to.strftime("%d/%m/%Y"),
        }
        async for item in self._paginate(
            endpoint="pedido.pesquisa.php",
            collection_key="pedidos",
            item_key="pedido",
            params=params,
        ):
            yield Order.model_validate(item)

    async def get(self, order_id: str) -> Order:
        """Fetches full order details (pedido.obter.php)."""
        retorno = await self._http.get("pedido.obter.php", {"id": order_id})
        return Order.model_validate(retorno["pedido"])
