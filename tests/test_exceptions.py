import pytest
from tiny_py.exceptions import (
    TinyError,
    TinyAPIError,
    TinyAuthError,
    TinyRateLimitError,
    TinyServerError,
    TinyTimeoutError,
)


def test_tiny_error_is_base_exception():
    err = TinyError("base error")
    assert isinstance(err, Exception)
    assert str(err) == "base error"


def test_tiny_api_error_stores_attributes():
    err = TinyAPIError("something failed", "/endpoint", ["err1", "err2"])
    assert str(err) == "something failed"
    assert err.endpoint == "/endpoint"
    assert err.errors == ["err1", "err2"]


def test_tiny_api_error_is_subclass_of_tiny_error():
    err = TinyAPIError("msg", "/ep", [])
    assert isinstance(err, TinyError)


def test_tiny_auth_error_is_subclass_of_tiny_api_error():
    err = TinyAuthError("invalid token", "/auth", ["token inválido"])
    assert isinstance(err, TinyAPIError)
    assert isinstance(err, TinyError)
    assert err.endpoint == "/auth"
    assert err.errors == ["token inválido"]


def test_tiny_rate_limit_error_is_subclass_of_tiny_error():
    err = TinyRateLimitError("rate limited")
    assert isinstance(err, TinyError)
    assert not isinstance(err, TinyAPIError)


def test_tiny_server_error_is_subclass_of_tiny_error():
    err = TinyServerError("server error")
    assert isinstance(err, TinyError)
    assert not isinstance(err, TinyAPIError)


def test_tiny_timeout_error_is_subclass_of_tiny_error():
    err = TinyTimeoutError("timed out")
    assert isinstance(err, TinyError)
    assert not isinstance(err, TinyAPIError)


def test_can_catch_tiny_api_error_via_tiny_error():
    with pytest.raises(TinyError):
        raise TinyAPIError("caught broadly", "/ep", [])


def test_tiny_api_error_empty_errors():
    err = TinyAPIError("no errors", "/ep", [])
    assert err.errors == []


def test_tiny_auth_error_inherits_init():
    err = TinyAuthError("expired", "/products", ["token expired"])
    assert str(err) == "expired"
    assert err.endpoint == "/products"
    assert err.errors == ["token expired"]
