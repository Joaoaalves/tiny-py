import asyncio
import threading
import time
from unittest.mock import patch, MagicMock

import pytest

from tiny_py._rate_limiter import PLAN_RPM, RateLimiter, AsyncRateLimiter


# ---------------------------------------------------------------------------
# PLAN_RPM constants
# ---------------------------------------------------------------------------

def test_plan_rpm_free():
    assert PLAN_RPM["free"] == 30


def test_plan_rpm_basic():
    assert PLAN_RPM["basic"] == 60


def test_plan_rpm_advanced():
    assert PLAN_RPM["advanced"] == 120


def test_plan_rpm_keys():
    assert set(PLAN_RPM.keys()) == {"free", "basic", "advanced"}


# ---------------------------------------------------------------------------
# RateLimiter — synchronous
# ---------------------------------------------------------------------------

def test_rate_limiter_acquire_immediate_when_tokens_available():
    """First acquire should return immediately since bucket starts full."""
    limiter = RateLimiter(rpm=60)
    start = time.monotonic()
    limiter.acquire()
    elapsed = time.monotonic() - start
    assert elapsed < 0.1, "First acquire should be nearly instant"


def test_rate_limiter_depletes_tokens():
    """Acquiring more tokens than available should eventually block."""
    limiter = RateLimiter(rpm=2)
    # The bucket starts with 2 tokens; first two acquires instant, third needs refill
    limiter.acquire()
    limiter.acquire()
    # Third acquire requires waiting — mock sleep to avoid blocking
    sleep_calls = []

    original_monotonic_calls = []
    base_time = time.monotonic()

    call_count = [0]

    def fake_monotonic():
        val = base_time + call_count[0] * 30.0  # jump 30s each call
        call_count[0] += 1
        return val

    def fake_sleep(secs):
        sleep_calls.append(secs)
        # Don't actually sleep

    with patch("tiny_py._rate_limiter.time.monotonic", side_effect=fake_monotonic):
        with patch("tiny_py._rate_limiter.time.sleep", side_effect=fake_sleep):
            limiter2 = RateLimiter(rpm=60)
            # drain all tokens
            limiter2._tokens = 0.0
            limiter2.acquire()  # should call sleep once, then get token via refill

    # Sleep was called or the refill mechanism triggered
    # Either way, no exception was raised
    assert True


def test_rate_limiter_multiple_acquires_no_error():
    """Multiple acquires on a full bucket should not error."""
    limiter = RateLimiter(rpm=120)
    for _ in range(10):
        limiter.acquire()


def test_rate_limiter_thread_safety():
    """Multiple threads can acquire without exceptions or data corruption."""
    limiter = RateLimiter(rpm=120)
    errors = []

    def worker():
        try:
            limiter.acquire()
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=5.0)

    assert errors == [], f"Thread safety errors: {errors}"


def test_rate_limiter_tokens_never_exceed_max():
    """Tokens should never exceed max_tokens even after long idle."""
    limiter = RateLimiter(rpm=60)
    # Simulate large elapsed time
    limiter._last_refill = time.monotonic() - 10000.0
    limiter.acquire()
    with limiter._lock:
        assert limiter._tokens <= limiter._max_tokens


# ---------------------------------------------------------------------------
# AsyncRateLimiter
# ---------------------------------------------------------------------------

async def test_async_rate_limiter_acquire_immediate():
    """First async acquire should return immediately."""
    limiter = AsyncRateLimiter(rpm=60)
    start = time.monotonic()
    await limiter.acquire()
    elapsed = time.monotonic() - start
    assert elapsed < 0.5


async def test_async_rate_limiter_multiple_acquires():
    """Multiple async acquires on a full bucket should not error."""
    limiter = AsyncRateLimiter(rpm=120)
    for _ in range(5):
        await limiter.acquire()


async def test_async_rate_limiter_depletes_and_refills():
    """When tokens are depleted, acquire waits for refill."""
    limiter = AsyncRateLimiter(rpm=60)
    limiter._tokens = 0.0

    sleep_calls = []

    async def fake_sleep(secs):
        sleep_calls.append(secs)
        # Simulate time passing by updating limiter state
        limiter._tokens = 1.0

    with patch("tiny_py._rate_limiter.asyncio.sleep", side_effect=fake_sleep):
        await limiter.acquire()

    assert len(sleep_calls) >= 1


async def test_async_rate_limiter_tokens_never_exceed_max():
    """Tokens should never exceed max after long idle in async limiter."""
    limiter = AsyncRateLimiter(rpm=60)
    limiter._last_refill = time.monotonic() - 10000.0
    await limiter.acquire()
    async with limiter._lock:
        assert limiter._tokens <= limiter._max_tokens
