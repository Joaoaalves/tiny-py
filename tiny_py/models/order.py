from datetime import date
from pydantic import BaseModel, Field, field_validator


class OrderItem(BaseModel):
    model_config = {"populate_by_name": True}

    product_id: str = Field(alias="id_produto")
    sku: str = Field(alias="codigo")
    description: str = Field(alias="descricao")
    quantity: float = Field(alias="quantidade")
    unit_price: float = Field(alias="valor_unitario")


class OrderEcommerce(BaseModel):
    model_config = {"populate_by_name": True}

    id: str
    name: str = Field(alias="nomeEcommerce")
    order_number: str = Field(alias="numeroPedidoEcommerce")


class Order(BaseModel):
    model_config = {"populate_by_name": True}

    id: str
    number: str = Field(alias="numero")
    order_date: date = Field(alias="data_pedido")
    status: str = Field(alias="situacao")
    items: list[OrderItem] = Field(alias="itens", default_factory=list)
    ecommerce: OrderEcommerce | None = Field(alias="ecommerce", default=None)
    total: float = Field(alias="total_pedido")
    tracking_code: str = Field(alias="codigo_rastreamento", default="")

    @field_validator("order_date", mode="before")
    @classmethod
    def parse_date(cls, v: object) -> date:
        if isinstance(v, str):
            from datetime import datetime
            return datetime.strptime(v, "%d/%m/%Y").date()
        return v  # type: ignore[return-value]
