import time
from typing import Any

import requests
from requests.adapters import HTTPAdapter as RequestsHTTPAdapter

from tiny_py._rate_limiter import RateLimiter
from tiny_py.exceptions import (
    TinyAPIError,
    TinyAuthError,
    TinyRateLimitError,
    TinyServerError,
    TinyTimeoutError,
)

_RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})


class HTTPAdapter:
    def __init__(
        self,
        token: str,
        rate_limiter: RateLimiter,
        timeout: tuple[float, float],
        max_retries: int,
        base_url: str,
    ) -> None:
        self._token = token
        self._rate_limiter = rate_limiter
        self._timeout = timeout
        self._max_retries = max_retries
        self._base_url = base_url.rstrip("/")
        self._session = self._build_session()

    def _build_session(self) -> requests.Session:
        session = requests.Session()
        adapter = RequestsHTTPAdapter(
            pool_connections=4,
            pool_maxsize=10,
        )
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def _url(self, endpoint: str) -> str:
        return f"{self._base_url}/{endpoint.lstrip('/')}"

    def _base_params(self) -> dict[str, str]:
        return {"token": self._token, "formato": "json"}

    def _parse_retorno(self, response: requests.Response, endpoint: str) -> dict[str, Any]:
        data: dict[str, Any] = response.json()
        retorno: dict[str, Any] = data.get("retorno", {})
        status = retorno.get("status", "").lower()
        if status != "ok":
            erros_raw = retorno.get("erros", [])
            errors: list[str] = []
            for e in erros_raw:
                if isinstance(e, dict):
                    errors.append(e.get("erro", str(e)))
                else:
                    errors.append(str(e))
            message = (
                errors[0]
                if errors
                else retorno.get("status_processamento", "Unknown error")
            )
            if any(
                "token" in err.lower()
                or "autenticação" in err.lower()
                or "autenticacao" in err.lower()
                for err in errors
            ):
                raise TinyAuthError(message, endpoint, errors)
            raise TinyAPIError(message, endpoint, errors)
        return retorno

    def _request_with_retry(
        self, method: str, endpoint: str, **kwargs: Any
    ) -> dict[str, Any]:
        url = self._url(endpoint)
        last_exc: Exception | None = None
        backoff = 1.0

        for attempt in range(self._max_retries + 1):
            if attempt > 0:
                time.sleep(backoff)
                backoff = min(backoff * 2, 60.0)

            self._rate_limiter.acquire()

            try:
                resp = self._session.request(
                    method, url, timeout=self._timeout, **kwargs
                )
            except requests.exceptions.Timeout as exc:
                last_exc = exc
                if attempt >= self._max_retries:
                    raise TinyTimeoutError(
                        f"Request to {endpoint} timed out"
                    ) from exc
                continue
            except requests.exceptions.RequestException as exc:
                raise TinyServerError(f"Request failed: {exc}") from exc

            if resp.status_code in _RETRYABLE_STATUS:
                if attempt < self._max_retries:
                    last_exc = (
                        TinyRateLimitError(f"Rate limit on {endpoint}")
                        if resp.status_code == 429
                        else TinyServerError(f"Server error on {endpoint}")
                    )
                    continue
                # Last attempt — raise the appropriate error
                if resp.status_code == 429:
                    raise TinyRateLimitError(
                        f"Rate limit exceeded on {endpoint} after {self._max_retries + 1} attempts"
                    )
                raise TinyServerError(
                    f"Server error {resp.status_code} on {endpoint} after {self._max_retries + 1} attempts"
                )

            # Non-retryable status: let _parse_retorno handle business errors
            # or raise for unexpected HTTP errors
            try:
                resp.raise_for_status()
            except requests.exceptions.HTTPError as exc:
                raise TinyServerError(f"HTTP error on {endpoint}: {exc}") from exc

            return self._parse_retorno(resp, endpoint)

        # Should never reach here but be safe
        if last_exc is not None:
            raise last_exc
        raise TinyServerError(
            f"All {self._max_retries + 1} attempts failed for {endpoint}"
        )

    def get(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        all_params = {**self._base_params(), **(params or {})}
        return self._request_with_retry("GET", endpoint, params=all_params)

    def post(
        self, endpoint: str, data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        all_params = self._base_params()
        return self._request_with_retry(
            "POST", endpoint, params=all_params, data=data or {}
        )

    def close(self) -> None:
        self._session.close()

    def __enter__(self) -> "HTTPAdapter":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
