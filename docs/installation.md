# Installation

## Requirements

- Python 3.11 or later
- pip

## Install from source

Clone the repository and install in editable mode:

```bash
git clone <repo-url>
cd tiny-client
pip install -e .
```

## Install with dev dependencies

```bash
pip install -e ".[dev]"
```

Dev extras include: `pytest`, `pytest-asyncio`, `responses`, `respx`, `pytest-httpserver`.

## Dependencies

| Package | Purpose |
|---------|---------|
| `requests>=2.31` | Sync HTTP (used by `TinyClient`) |
| `httpx>=0.27` | Async HTTP (used by `AsyncTinyClient`) |
| `pydantic>=2.0` | Model validation and serialisation |

## Verify installation

```python
from tiny_py import TinyClient, AsyncTinyClient
print("tiny-py ready")
```
