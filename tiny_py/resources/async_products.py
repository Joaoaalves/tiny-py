import json
from collections.abc import AsyncIterator

from tiny_py.models.product import (
    PriceUpdateRequest,
    Product,
    ProductStock,
    StockUpdateRequest,
)
from tiny_py.resources._async_base import AsyncBaseResource


class AsyncProductsResource(AsyncBaseResource):
    async def search(self, situacao: str = "A") -> list[Product]:
        """Returns all products matching the filter (auto-paginated)."""
        return [p async for p in self.iter_search(situacao=situacao)]

    async def iter_search(self, situacao: str = "A") -> AsyncIterator[Product]:
        """Memory-efficient async generator. Preferred for large catalogues."""
        async for item in self._paginate(
            endpoint="produto.pesquisa.php",
            collection_key="produtos",
            item_key="produto",
            params={"situacao": situacao},
        ):
            yield Product.model_validate(item)

    async def get(self, product_id: str) -> Product:
        """Fetches full product data (produto.obter.php)."""
        retorno = await self._http.get("produto.obter.php", {"id": product_id})
        return Product.model_validate(retorno["produto"])

    async def get_stock(self, product_id: str) -> ProductStock:
        """Fetches stock per deposit (produto.obter.estoque.php)."""
        retorno = await self._http.get("produto.obter.estoque.php", {"id": product_id})
        return ProductStock.model_validate(retorno["produto"])

    async def update_stock(self, product_id: str, request: StockUpdateRequest) -> None:
        """Updates deposit balances (produto.atualizar.estoque.php)."""
        deposits_data = [
            {"idDeposito": d.deposit_id, "saldo": d.balance}
            for d in request.deposits
        ]
        await self._http.post(
            "produto.atualizar.estoque.php",
            {
                "id": product_id,
                "depositos": json.dumps(deposits_data),
            },
        )

    async def update_price(self, product_id: str, request: PriceUpdateRequest) -> None:
        """Updates regular and promotional prices (produto.atualizar.preco.php)."""
        data: dict = {"id": product_id, "preco": request.price}
        if request.promo_price is not None:
            data["preco_promocional"] = request.promo_price
        await self._http.post("produto.atualizar.preco.php", data)
