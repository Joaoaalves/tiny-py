import json
from collections.abc import Iterator

from tiny_py._http import HTTPAdapter
from tiny_py.models.product import (
    PriceUpdateRequest,
    Product,
    ProductStock,
    StockUpdateRequest,
)
from tiny_py.resources._base import BaseResource


class ProductsResource(BaseResource):
    def search(self, situacao: str = "A") -> list[Product]:
        """Returns all products matching the filter (auto-paginated)."""
        return list(self.iter_search(situacao=situacao))

    def iter_search(self, situacao: str = "A") -> Iterator[Product]:
        """Memory-efficient generator. Preferred for large catalogues."""
        for item in self._paginate(
            endpoint="produto.pesquisa.php",
            collection_key="produtos",
            item_key="produto",
            params={"situacao": situacao},
        ):
            yield Product.model_validate(item)

    def get(self, product_id: str) -> Product:
        """Fetches full product data (produto.obter.php)."""
        retorno = self._http.get("produto.obter.php", {"id": product_id})
        return Product.model_validate(retorno["produto"])

    def get_stock(self, product_id: str) -> ProductStock:
        """Fetches stock per deposit (produto.obter.estoque.php)."""
        retorno = self._http.get("produto.obter.estoque.php", {"id": product_id})
        return ProductStock.model_validate(retorno["produto"])

    def update_stock(self, product_id: str, request: StockUpdateRequest) -> None:
        """Updates deposit balances (produto.atualizar.estoque.php)."""
        deposits_data = [
            {"idDeposito": d.deposit_id, "saldo": d.balance}
            for d in request.deposits
        ]
        self._http.post(
            "produto.atualizar.estoque.php",
            {
                "id": product_id,
                "depositos": json.dumps(deposits_data),
            },
        )

    def update_price(self, product_id: str, request: PriceUpdateRequest) -> None:
        """Updates regular and promotional prices (produto.atualizar.preco.php)."""
        data: dict = {"id": product_id, "preco": request.price}
        if request.promo_price is not None:
            data["preco_promocional"] = request.promo_price
        self._http.post("produto.atualizar.preco.php", data)
