from typing import TYPE_CHECKING, Literal

from tiny_py._http import HTTPAdapter
from tiny_py._rate_limiter import PLAN_RPM, AsyncRateLimiter, RateLimiter
from tiny_py.resources.orders import OrdersResource
from tiny_py.resources.products import ProductsResource

if TYPE_CHECKING:
    from tiny_py._async_http import AsyncHTTPAdapter
    from tiny_py.resources.async_orders import AsyncOrdersResource
    from tiny_py.resources.async_products import AsyncProductsResource

Plan = Literal["free", "basic", "advanced"]

DEFAULT_BASE_URL = "https://api.tiny.com.br/api2"
DEFAULT_TIMEOUT: tuple[float, float] = (5.0, 30.0)
DEFAULT_MAX_RETRIES = 3


class TinyClient:
    def __init__(
        self,
        token: str,
        plan: Plan = "advanced",
        timeout: tuple[float, float] = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        base_url: str = DEFAULT_BASE_URL,
    ) -> None:
        rpm = PLAN_RPM[plan]
        self._http = HTTPAdapter(
            token=token,
            rate_limiter=RateLimiter(rpm),
            timeout=timeout,
            max_retries=max_retries,
            base_url=base_url,
        )
        self._products: ProductsResource | None = None
        self._orders: OrdersResource | None = None

    @property
    def products(self) -> ProductsResource:
        if self._products is None:
            self._products = ProductsResource(self._http)
        return self._products

    @property
    def orders(self) -> OrdersResource:
        if self._orders is None:
            self._orders = OrdersResource(self._http)
        return self._orders

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "TinyClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


class AsyncTinyClient:
    def __init__(
        self,
        token: str,
        plan: Plan = "advanced",
        timeout: tuple[float, float] = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        base_url: str = DEFAULT_BASE_URL,
    ) -> None:
        from tiny_py._async_http import AsyncHTTPAdapter

        rpm = PLAN_RPM[plan]
        self._http: AsyncHTTPAdapter = AsyncHTTPAdapter(
            token=token,
            rate_limiter=AsyncRateLimiter(rpm),
            timeout=timeout,
            max_retries=max_retries,
            base_url=base_url,
        )
        self._products: AsyncProductsResource | None = None
        self._orders: AsyncOrdersResource | None = None

    @property
    def products(self) -> "AsyncProductsResource":
        if self._products is None:
            from tiny_py.resources.async_products import AsyncProductsResource
            self._products = AsyncProductsResource(self._http)
        return self._products

    @property
    def orders(self) -> "AsyncOrdersResource":
        if self._orders is None:
            from tiny_py.resources.async_orders import AsyncOrdersResource
            self._orders = AsyncOrdersResource(self._http)
        return self._orders

    async def close(self) -> None:
        await self._http.close()

    async def __aenter__(self) -> "AsyncTinyClient":
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()
