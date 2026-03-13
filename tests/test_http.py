import json
from unittest.mock import patch, MagicMock

import pytest
import responses as responses_lib

from tiny_py._http import HTTPAdapter
from tiny_py._rate_limiter import RateLimiter
from tiny_py.exceptions import (
    TinyAPIError,
    TinyAuthError,
    TinyRateLimitError,
    TinyServerError,
    TinyTimeoutError,
)

BASE_URL = "http://test.local/api2"
TOKEN = "test-token"


def make_adapter(max_retries: int = 0) -> HTTPAdapter:
    limiter = MagicMock(spec=RateLimiter)
    limiter.acquire.return_value = None
    return HTTPAdapter(
        token=TOKEN,
        rate_limiter=limiter,
        timeout=(5.0, 30.0),
        max_retries=max_retries,
        base_url=BASE_URL,
    )


def ok_response(data: dict) -> dict:
    return {"retorno": {"status": "OK", **data}}


def error_response(errors: list[str], status_processamento: str = "2") -> dict:
    return {
        "retorno": {
            "status": "Erro",
            "status_processamento": status_processamento,
            "erros": [{"erro": e} for e in errors],
        }
    }


# ---------------------------------------------------------------------------
# Successful GET
# ---------------------------------------------------------------------------

@responses_lib.activate
def test_get_success_returns_retorno():
    responses_lib.add(
        responses_lib.GET,
        f"{BASE_URL}/produto.pesquisa.php",
        json=ok_response({"produtos": []}),
        status=200,
    )
    adapter = make_adapter()
    result = adapter.get("produto.pesquisa.php", {"situacao": "A"})
    assert result["status"] == "OK"
    assert "produtos" in result


@responses_lib.activate
def test_get_injects_token_and_formato():
    responses_lib.add(
        responses_lib.GET,
        f"{BASE_URL}/produto.pesquisa.php",
        json=ok_response({}),
        status=200,
    )
    adapter = make_adapter()
    adapter.get("produto.pesquisa.php")
    req = responses_lib.calls[0].request
    assert "token=test-token" in req.url
    assert "formato=json" in req.url


# ---------------------------------------------------------------------------
# Successful POST
# ---------------------------------------------------------------------------

@responses_lib.activate
def test_post_success_returns_retorno():
    responses_lib.add(
        responses_lib.POST,
        f"{BASE_URL}/produto.atualizar.preco.php",
        json=ok_response({}),
        status=200,
    )
    adapter = make_adapter()
    result = adapter.post("produto.atualizar.preco.php", {"id": "1", "preco": "29.99"})
    assert result["status"] == "OK"


# ---------------------------------------------------------------------------
# API error (status != OK) -> TinyAPIError
# ---------------------------------------------------------------------------

@responses_lib.activate
def test_api_error_raises_tiny_api_error():
    responses_lib.add(
        responses_lib.GET,
        f"{BASE_URL}/produto.obter.php",
        json=error_response(["Produto não encontrado"]),
        status=200,
    )
    adapter = make_adapter()
    with pytest.raises(TinyAPIError) as exc_info:
        adapter.get("produto.obter.php", {"id": "999"})
    assert "Produto não encontrado" in str(exc_info.value)
    assert exc_info.value.endpoint == "produto.obter.php"


@responses_lib.activate
def test_api_error_stores_errors_list():
    responses_lib.add(
        responses_lib.GET,
        f"{BASE_URL}/produto.obter.php",
        json=error_response(["Error 1", "Error 2"]),
        status=200,
    )
    adapter = make_adapter()
    with pytest.raises(TinyAPIError) as exc_info:
        adapter.get("produto.obter.php", {"id": "999"})
    assert exc_info.value.errors == ["Error 1", "Error 2"]


# ---------------------------------------------------------------------------
# Auth error
# ---------------------------------------------------------------------------

@responses_lib.activate
def test_auth_error_raises_tiny_auth_error():
    responses_lib.add(
        responses_lib.GET,
        f"{BASE_URL}/produto.obter.php",
        json=error_response(["token inválido"]),
        status=200,
    )
    adapter = make_adapter()
    with pytest.raises(TinyAuthError):
        adapter.get("produto.obter.php", {"id": "1"})


@responses_lib.activate
def test_auth_error_autenticacao_keyword():
    responses_lib.add(
        responses_lib.GET,
        f"{BASE_URL}/produto.obter.php",
        json=error_response(["Falha na autenticacao do usuário"]),
        status=200,
    )
    adapter = make_adapter()
    with pytest.raises(TinyAuthError):
        adapter.get("produto.obter.php", {"id": "1"})


# ---------------------------------------------------------------------------
# HTTP 429 -> TinyRateLimitError after retries exhausted
# ---------------------------------------------------------------------------

@responses_lib.activate
@patch("tiny_py._http.time.sleep")
def test_429_raises_rate_limit_error_after_retries(mock_sleep):
    for _ in range(3):  # max_retries=2 means 3 total attempts
        responses_lib.add(
            responses_lib.GET,
            f"{BASE_URL}/produto.pesquisa.php",
            status=429,
        )
    adapter = make_adapter(max_retries=2)
    with pytest.raises(TinyRateLimitError):
        adapter.get("produto.pesquisa.php")
    assert mock_sleep.call_count == 2  # sleeps between retries


# ---------------------------------------------------------------------------
# HTTP 500 -> TinyServerError after retries exhausted
# ---------------------------------------------------------------------------

@responses_lib.activate
@patch("tiny_py._http.time.sleep")
def test_500_raises_server_error_after_retries(mock_sleep):
    for _ in range(3):
        responses_lib.add(
            responses_lib.GET,
            f"{BASE_URL}/produto.pesquisa.php",
            status=500,
        )
    adapter = make_adapter(max_retries=2)
    with pytest.raises(TinyServerError):
        adapter.get("produto.pesquisa.php")


# ---------------------------------------------------------------------------
# Retry logic: succeeds on second attempt after 500
# ---------------------------------------------------------------------------

@responses_lib.activate
@patch("tiny_py._http.time.sleep")
def test_retry_succeeds_on_second_attempt(mock_sleep):
    responses_lib.add(
        responses_lib.GET,
        f"{BASE_URL}/produto.pesquisa.php",
        status=500,
    )
    responses_lib.add(
        responses_lib.GET,
        f"{BASE_URL}/produto.pesquisa.php",
        json=ok_response({"produtos": []}),
        status=200,
    )
    adapter = make_adapter(max_retries=2)
    result = adapter.get("produto.pesquisa.php")
    assert result["status"] == "OK"
    assert mock_sleep.call_count == 1  # one sleep before second attempt


# ---------------------------------------------------------------------------
# Timeout -> TinyTimeoutError
# ---------------------------------------------------------------------------

@patch("tiny_py._http.time.sleep")
def test_timeout_raises_tiny_timeout_error(mock_sleep):
    import requests as req_lib
    adapter = make_adapter(max_retries=1)
    with patch.object(adapter._session, "request", side_effect=req_lib.exceptions.Timeout):
        with pytest.raises(TinyTimeoutError):
            adapter.get("produto.pesquisa.php")
    assert mock_sleep.call_count == 1


# ---------------------------------------------------------------------------
# close() and context manager
# ---------------------------------------------------------------------------

def test_close_works():
    adapter = make_adapter()
    adapter.close()  # should not raise


def test_context_manager():
    adapter = make_adapter()
    with adapter as a:
        assert a is adapter
    # After __exit__, session is closed — no exception raised


@responses_lib.activate
def test_context_manager_closes_on_exit():
    responses_lib.add(
        responses_lib.GET,
        f"{BASE_URL}/produto.pesquisa.php",
        json=ok_response({}),
        status=200,
    )
    with make_adapter() as adapter:
        adapter.get("produto.pesquisa.php")
    # No assertion needed — just verifying no exceptions


# ---------------------------------------------------------------------------
# Exponential backoff verification
# ---------------------------------------------------------------------------

@responses_lib.activate
@patch("tiny_py._http.time.sleep")
def test_exponential_backoff_delays(mock_sleep):
    for _ in range(4):
        responses_lib.add(
            responses_lib.GET,
            f"{BASE_URL}/produto.pesquisa.php",
            status=503,
        )
    adapter = make_adapter(max_retries=3)
    with pytest.raises(TinyServerError):
        adapter.get("produto.pesquisa.php")
    # Should have slept 3 times (between 4 attempts)
    assert mock_sleep.call_count == 3
    # Check backoff increases: 1.0, 2.0, 4.0
    delays = [call.args[0] for call in mock_sleep.call_args_list]
    assert delays[0] == 1.0
    assert delays[1] == 2.0
    assert delays[2] == 4.0


# ---------------------------------------------------------------------------
# Rate limiter is called on each request
# ---------------------------------------------------------------------------

@responses_lib.activate
def test_rate_limiter_acquire_called():
    responses_lib.add(
        responses_lib.GET,
        f"{BASE_URL}/produto.pesquisa.php",
        json=ok_response({}),
        status=200,
    )
    limiter = MagicMock(spec=RateLimiter)
    adapter = HTTPAdapter(
        token=TOKEN,
        rate_limiter=limiter,
        timeout=(5.0, 30.0),
        max_retries=0,
        base_url=BASE_URL,
    )
    adapter.get("produto.pesquisa.php")
    limiter.acquire.assert_called_once()
