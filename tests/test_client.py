import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from tiny_py import TinyClient, AsyncTinyClient
from tiny_py._client import DEFAULT_BASE_URL, DEFAULT_TIMEOUT, DEFAULT_MAX_RETRIES
from tiny_py.resources.products import ProductsResource
from tiny_py.resources.orders import OrdersResource


# ---------------------------------------------------------------------------
# TinyClient instantiation
# ---------------------------------------------------------------------------

def test_tiny_client_instantiates_with_defaults():
    client = TinyClient(token="test-token")
    assert client is not None
    client.close()


def test_tiny_client_instantiates_with_all_params():
    client = TinyClient(
        token="test-token",
        plan="basic",
        timeout=(3.0, 10.0),
        max_retries=2,
        base_url="http://localhost:8080/api2",
    )
    assert client is not None
    client.close()


def test_tiny_client_invalid_plan_raises():
    with pytest.raises(KeyError):
        TinyClient(token="test-token", plan="enterprise")  # type: ignore


# ---------------------------------------------------------------------------
# TinyClient.products
# ---------------------------------------------------------------------------

def test_tiny_client_products_is_products_resource():
    client = TinyClient(token="test-token")
    assert isinstance(client.products, ProductsResource)
    client.close()


def test_tiny_client_products_lazily_instantiated():
    client = TinyClient(token="test-token")
    # First access creates the resource
    resource1 = client.products
    # Second access returns the same instance
    resource2 = client.products
    assert resource1 is resource2
    client.close()


# ---------------------------------------------------------------------------
# TinyClient.orders
# ---------------------------------------------------------------------------

def test_tiny_client_orders_is_orders_resource():
    client = TinyClient(token="test-token")
    assert isinstance(client.orders, OrdersResource)
    client.close()


def test_tiny_client_orders_lazily_instantiated():
    client = TinyClient(token="test-token")
    resource1 = client.orders
    resource2 = client.orders
    assert resource1 is resource2
    client.close()


# ---------------------------------------------------------------------------
# TinyClient context manager
# ---------------------------------------------------------------------------

def test_tiny_client_context_manager():
    with TinyClient(token="test-token") as client:
        assert client is not None
        assert isinstance(client.products, ProductsResource)
    # After exiting, no exception should be raised


def test_tiny_client_context_manager_calls_close():
    client = TinyClient(token="test-token")
    with patch.object(client, "close") as mock_close:
        with client:
            pass
        mock_close.assert_called_once()


# ---------------------------------------------------------------------------
# TinyClient plan-based rate limiting
# ---------------------------------------------------------------------------

def test_tiny_client_free_plan():
    client = TinyClient(token="test-token", plan="free")
    assert client is not None
    client.close()


def test_tiny_client_basic_plan():
    client = TinyClient(token="test-token", plan="basic")
    assert client is not None
    client.close()


def test_tiny_client_advanced_plan():
    client = TinyClient(token="test-token", plan="advanced")
    assert client is not None
    client.close()


# ---------------------------------------------------------------------------
# AsyncTinyClient instantiation
# ---------------------------------------------------------------------------

async def test_async_tiny_client_instantiates():
    client = AsyncTinyClient(token="test-token")
    assert client is not None
    await client.close()


async def test_async_tiny_client_with_all_params():
    client = AsyncTinyClient(
        token="test-token",
        plan="basic",
        timeout=(3.0, 10.0),
        max_retries=2,
        base_url="http://localhost:8080/api2",
    )
    assert client is not None
    await client.close()


async def test_async_tiny_client_invalid_plan_raises():
    with pytest.raises(KeyError):
        AsyncTinyClient(token="test-token", plan="enterprise")  # type: ignore


# ---------------------------------------------------------------------------
# AsyncTinyClient.products and .orders
# ---------------------------------------------------------------------------

async def test_async_tiny_client_products_resource():
    from tiny_py.resources.async_products import AsyncProductsResource
    client = AsyncTinyClient(token="test-token")
    assert isinstance(client.products, AsyncProductsResource)
    await client.close()


async def test_async_tiny_client_orders_resource():
    from tiny_py.resources.async_orders import AsyncOrdersResource
    client = AsyncTinyClient(token="test-token")
    assert isinstance(client.orders, AsyncOrdersResource)
    await client.close()


async def test_async_tiny_client_products_lazily_instantiated():
    client = AsyncTinyClient(token="test-token")
    resource1 = client.products
    resource2 = client.products
    assert resource1 is resource2
    await client.close()


async def test_async_tiny_client_orders_lazily_instantiated():
    client = AsyncTinyClient(token="test-token")
    resource1 = client.orders
    resource2 = client.orders
    assert resource1 is resource2
    await client.close()


# ---------------------------------------------------------------------------
# AsyncTinyClient context manager
# ---------------------------------------------------------------------------

async def test_async_tiny_client_async_context_manager():
    async with AsyncTinyClient(token="test-token") as client:
        assert client is not None


async def test_async_tiny_client_context_manager_calls_close():
    client = AsyncTinyClient(token="test-token")
    original_close = client.close
    close_called = []

    async def mock_close():
        close_called.append(True)
        await original_close()

    client.close = mock_close  # type: ignore
    async with client:
        pass
    assert len(close_called) == 1


# ---------------------------------------------------------------------------
# Module-level imports
# ---------------------------------------------------------------------------

def test_imports_from_package():
    import tiny_py
    assert hasattr(tiny_py, "TinyClient")
    assert hasattr(tiny_py, "AsyncTinyClient")
    assert hasattr(tiny_py, "exceptions")
    assert hasattr(tiny_py, "models")


def test_exceptions_importable():
    from tiny_py import exceptions
    assert hasattr(exceptions, "TinyError")
    assert hasattr(exceptions, "TinyAPIError")
    assert hasattr(exceptions, "TinyAuthError")
    assert hasattr(exceptions, "TinyRateLimitError")
    assert hasattr(exceptions, "TinyServerError")
    assert hasattr(exceptions, "TinyTimeoutError")


def test_models_importable():
    from tiny_py import models
    assert hasattr(models, "Product")
    assert hasattr(models, "Order")
    assert hasattr(models, "ProductStock")
