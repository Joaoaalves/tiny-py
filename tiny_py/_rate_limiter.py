import asyncio
import threading
import time

PLAN_RPM: dict[str, int] = {
    "free": 30,
    "basic": 60,
    "advanced": 120,
}


class RateLimiter:
    """Thread-safe token bucket for synchronous use."""

    def __init__(self, rpm: int) -> None:
        self._rate = rpm / 60.0  # tokens per second
        self._tokens: float = float(rpm)
        self._max_tokens: float = float(rpm)
        self._last_refill: float = time.monotonic()
        self._lock = threading.Lock()

    def acquire(self) -> None:
        """Block until a token is available."""
        while True:
            with self._lock:
                now = time.monotonic()
                elapsed = now - self._last_refill
                self._tokens = min(
                    self._max_tokens,
                    self._tokens + elapsed * self._rate,
                )
                self._last_refill = now
                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    return
                wait = (1.0 - self._tokens) / self._rate
            time.sleep(wait)


class AsyncRateLimiter:
    """asyncio-safe token bucket for async use."""

    def __init__(self, rpm: int) -> None:
        self._rate = rpm / 60.0
        self._tokens: float = float(rpm)
        self._max_tokens: float = float(rpm)
        self._last_refill: float = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Async-safe wait until a token is available."""
        while True:
            async with self._lock:
                now = time.monotonic()
                elapsed = now - self._last_refill
                self._tokens = min(
                    self._max_tokens,
                    self._tokens + elapsed * self._rate,
                )
                self._last_refill = now
                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    return
                wait = (1.0 - self._tokens) / self._rate
            await asyncio.sleep(wait)
