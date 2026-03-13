# Rate Limiting

tiny-py includes a **token bucket** rate limiter per client instance. It enforces the plan's requests-per-minute limit before every outgoing request.

## Plan defaults

```python
PLAN_RPM = {
    "free":     30,   # 0.5 req/s
    "basic":    60,   # 1 req/s
    "advanced": 120,  # 2 req/s
}
```

The limiter is created automatically based on the `plan` parameter:

```python
client = TinyClient(token="...", plan="advanced")
# → RateLimiter(rpm=120) created internally
```

---

## How it works

### Token bucket

- The bucket starts full (capacity = RPM).
- Each request consumes one token.
- Tokens refill at a constant rate (`rpm / 60` tokens per second).
- If no token is available, `acquire()` **blocks** (sync) or **awaits** (async) until one becomes available.
- Blocking is preferred over dropping requests — the caller never has to retry due to the limiter itself.

---

## Sync vs async

| Class | Used by | Thread-safe |
|-------|---------|-------------|
| `RateLimiter` | `TinyClient` | Yes (`threading.Lock`) |
| `AsyncRateLimiter` | `AsyncTinyClient` | Yes (`asyncio.Lock`) |

---

## Multi-process workers

Each process has its **own** `TinyClient` instance with its own in-memory limiter. If you run many workers against the same Tiny token, the per-process limiters are not coordinated:

```
Process A → RateLimiter(120 rpm)   ┐
Process B → RateLimiter(120 rpm)   ├── Combined: 240+ rpm → 429s
Process C → RateLimiter(120 rpm)   ┘
```

### Solution: Redis-backed sliding window

For high-concurrency scenarios, replace the in-process limiter with a shared Redis counter. Pass a lower per-process `rpm` as a workaround in the meantime:

```python
# 3 workers sharing a 120 rpm limit → 40 rpm per worker
client = TinyClient(token="...", plan="free")  # rpm=30 is safe for 4 workers
```

Or implement a custom limiter that uses `redis-py` with a Lua sliding window script and pass the custom `rpm` override accordingly.

---

## Observing throttling

When the limiter is actively throttling, `acquire()` sleeps internally — no exception is raised. If the Tiny API still returns 429 (server-side limit tighter than expected), the HTTP layer retries with exponential backoff before raising `TinyRateLimitError`.
