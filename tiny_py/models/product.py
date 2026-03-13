from pydantic import BaseModel, Field, field_validator


class StockDeposit(BaseModel):
    model_config = {"populate_by_name": True}

    name: str = Field(alias="nome")
    balance: float = Field(alias="saldo")
    ignore: bool = Field(alias="desconsiderar")
    company: str = Field(alias="empresa")

    @field_validator("ignore", mode="before")
    @classmethod
    def parse_sn(cls, v: object) -> bool:
        if isinstance(v, str):
            return v.upper() == "S"
        return bool(v)


class StockDepositUpdate(BaseModel):
    model_config = {"populate_by_name": True}

    deposit_id: str = Field(alias="idDeposito")
    balance: float = Field(alias="saldo")


class ProductStock(BaseModel):
    model_config = {"populate_by_name": True}

    product_id: str = Field(alias="id")
    sku: str = Field(alias="codigo")
    name: str = Field(alias="nome")
    balance: float = Field(alias="saldo")
    reserved_balance: float = Field(alias="saldoReservado")
    deposits: list[StockDeposit] = Field(alias="depositos", default_factory=list)


class Product(BaseModel):
    model_config = {"populate_by_name": True}

    id: str
    name: str = Field(alias="nome")
    sku: str = Field(alias="codigo")
    price: float = Field(alias="preco")
    promo_price: float | None = Field(alias="preco_promocional", default=None)
    cost_price: float | None = Field(alias="preco_custo", default=None)
    unit: str = Field(alias="unidade")
    gtin: str | None = Field(alias="gtin", default=None)
    ncm: str | None = Field(alias="ncm", default=None)
    status: str = Field(alias="situacao")
    category: str | None = Field(alias="categoria", default=None)
    brand: str | None = Field(alias="marca", default=None)


class StockUpdateRequest(BaseModel):
    deposits: list[StockDepositUpdate]


class PriceUpdateRequest(BaseModel):
    price: float
    promo_price: float | None = None
