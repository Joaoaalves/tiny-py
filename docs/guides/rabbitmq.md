# RabbitMQ Workers

Use `TinyClient` (sync) in workers. One instance per process — never shared across process boundaries.

## Basic pattern

```python
# worker.py
import os
from tiny_py import TinyClient
from tiny_py.exceptions import TinyAPIError, TinyRateLimitError, TinyServerError, TinyTimeoutError

client = TinyClient(token=os.environ["TINY_TOKEN"], plan="advanced")

def handle_message(body: dict) -> None:
    try:
        order = client.orders.get(body["order_id"])
        publish_result(order)
    except TinyAPIError:
        nack(requeue=False)    # business error → Dead Letter Queue
    except (TinyRateLimitError, TinyServerError, TinyTimeoutError):
        nack(requeue=True)     # transient error → re-enqueue with backoff
```

---

## Exception routing

| Exception | `requeue` | Reason |
|-----------|-----------|--------|
| `TinyAPIError` | `False` | Same request will fail again |
| `TinyAuthError` | `False` | Invalid token — manual fix needed |
| `TinyRateLimitError` | `True` | Retry after backoff |
| `TinyServerError` | `True` | Transient server issue |
| `TinyTimeoutError` | `True` | Transient network issue |

---

## With pika

```python
import pika
import json
import os
from tiny_py import TinyClient
from tiny_py.exceptions import TinyAPIError, TinyRateLimitError, TinyServerError, TinyTimeoutError

client = TinyClient(token=os.environ["TINY_TOKEN"], plan="advanced")

def callback(ch, method, properties, body):
    message = json.loads(body)
    try:
        order = client.orders.get(message["order_id"])
        # ... process order ...
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except TinyAPIError:
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    except (TinyRateLimitError, TinyServerError, TinyTimeoutError):
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

connection = pika.BlockingConnection(pika.URLParameters(os.environ["RABBITMQ_URL"]))
channel = connection.channel()
channel.basic_consume(queue="orders", on_message_callback=callback)
channel.start_consuming()
```

---

## With Celery

```python
# tasks.py
import os
from celery import Celery
from tiny_py import TinyClient
from tiny_py.exceptions import TinyAPIError, TinyRateLimitError, TinyServerError, TinyTimeoutError

app = Celery("tasks", broker=os.environ["RABBITMQ_URL"])

# One client per worker process — created at module level
_client = TinyClient(token=os.environ["TINY_TOKEN"], plan="advanced")

@app.task(
    autoretry_for=(TinyRateLimitError, TinyServerError, TinyTimeoutError),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
)
def sync_order(order_id: str) -> dict:
    order = _client.orders.get(order_id)
    return order.model_dump()
```

---

## Multi-process rate limiting

Each worker process has its own `TinyClient` and its own in-memory rate limiter. If you run many workers against the same Tiny token, reduce the effective RPM per worker:

```python
# 4 workers × 30 rpm = 120 rpm total (safe for "advanced" plan)
client = TinyClient(token=..., plan="free")  # plan="free" → 30 rpm
```

For true coordination across processes, implement a Redis-backed sliding window and override `rpm` accordingly.
