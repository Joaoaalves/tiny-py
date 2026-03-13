import asyncio
import time
from typing import Any

import httpx

from tiny_py._rate_limiter import AsyncRateLimiter
from tiny_py.exceptions import (
    TinyAPIError,
    TinyAuthError,
    TinyRateLimitError,
    TinyServerError,
    TinyTimeoutError,
)

_RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})


class AsyncHTTPAdapter:
    def __init__(
        self,
        token: str,
        rate_limiter: AsyncRateLimiter,
        timeout: tuple[float, float],
        max_retries: int,
        base_url: str,
    ) -> None:
        self._token = token
        self._rate_limiter = rate_limiter
        self._timeout = httpx.Timeout(timeout[1], connect=timeout[0])
        self._max_retries = max_retries
        self._base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient()

    def _url(self, endpoint: str) -> str:
        return f"{self._base_url}/{endpoint.lstrip('/')}"

    def _base_params(self) -> dict[str, str]:
        return {"token": self._token, "formato": "json"}

    def _parse_retorno(self, data: dict[str, Any], endpoint: str) -> dict[str, Any]:
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
            message = errors[0] if errors else "Unknown error"
            if any(
                "token" in err.lower()
                or "autenticação" in err.lower()
                or "autenticacao" in err.lower()
                for err in errors
            ):
                raise TinyAuthError(message, endpoint, errors)
            raise TinyAPIError(message, endpoint, errors)
        return retorno

    async def _request_with_retry(
        self, method: str, endpoint: str, **kwargs: Any
    ) -> dict[str, Any]:
        url = self._url(endpoint)
        backoff = 1.0
        last_exc: Exception | None = None

        for attempt in range(self._max_retries + 1):
            if attempt > 0:
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 60.0)

            await self._rate_limiter.acquire()

            try:
                resp = await self._client.request(
                    method, url, timeout=self._timeout, **kwargs
                )
            except httpx.TimeoutException as exc:
                last_exc = exc
                if attempt >= self._max_retries:
                    raise TinyTimeoutError(
                        f"Request to {endpoint} timed out"
                    ) from exc
                continue
            except httpx.RequestError as exc:
                raise TinyServerError(f"Request failed: {exc}") from exc

            if resp.status_code in _RETRYABLE_STATUS:
                if attempt < self._max_retries:
                    last_exc = (
                        TinyRateLimitError(f"Rate limit on {endpoint}")
                        if resp.status_code == 429
                        else TinyServerError(f"Server error on {endpoint}")
                    )
                    continue
                if resp.status_code == 429:
                    raise TinyRateLimitError(
                        f"Rate limit exceeded on {endpoint} after {self._max_retries + 1} attempts"
                    )
                raise TinyServerError(
                    f"Server error {resp.status_code} on {endpoint} after {self._max_retries + 1} attempts"
                )

            try:
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                raise TinyServerError(f"HTTP error on {endpoint}: {exc}") from exc

            return self._parse_retorno(resp.json(), endpoint)

        if last_exc is not None:
            raise last_exc
        raise TinyServerError(
            f"All {self._max_retries + 1} attempts failed for {endpoint}"
        )

    async def get(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        all_params = {**self._base_params(), **(params or {})}
        return await self._request_with_retry("GET", endpoint, params=all_params)

    async def post(
        self, endpoint: str, data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        all_params = self._base_params()
        return await self._request_with_retry(
            "POST", endpoint, params=all_params, data=data or {}
        )

    async def close(self) -> None:
        await self._client.aclose()
