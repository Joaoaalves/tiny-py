# Claude Code Skill

tiny-erp-py ships a [Claude Code](https://claude.ai/claude-code) skill that teaches Claude how to use this library.

When active, Claude will:
- Know exactly which documentation page to fetch for each type of question
- Fetch **only** the relevant page — not the entire docs
- Apply hard-coded rules (correct import name, type constraints, retry logic) without any lookup

---

## Install

### Option A — one-liner (recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/joaoaalves/tiny-py/main/.claude/commands/tiny.md \
  -o ~/.claude/commands/tiny.md
```

Creates `~/.claude/commands/tiny.md`. The skill is available globally in all your projects.

### Option B — project-scoped

If you only want the skill inside a specific project:

```bash
mkdir -p .claude/commands
curl -fsSL https://raw.githubusercontent.com/joaoaalves/tiny-py/main/.claude/commands/tiny.md \
  -o .claude/commands/tiny.md
```

Commit the file so your whole team gets it automatically when they clone the repo.

### Option C — clone and copy

```bash
git clone https://github.com/joaoaalves/tiny-py.git
cp tiny-py/.claude/commands/tiny.md ~/.claude/commands/tiny.md
```

---

## Usage

After installing, start any Claude Code session and type:

```
/tiny
```

Then describe what you need:

```
/tiny How do I stream all active products and update their stock?
/tiny Show me the FastAPI dependency pattern for AsyncTinyClient
/tiny What should I catch in a RabbitMQ worker?
```

Claude will fetch only the relevant documentation page and answer based on it.

---

## What the skill knows without fetching

These rules are baked into the skill and applied immediately, with no network call:

| Rule | Detail |
|------|--------|
| Correct import | `from tiny_py import ...` — never `import tiny_erp_py` |
| Date params | `orders.search()` requires `datetime.date`, not strings |
| Return types | `update_stock()` and `update_price()` return `None` |
| Large datasets | Use `iter_search()`, not `search()` |
| Deposit totals | Filter `if not d.ignore` before summing balances |
| Retry logic | Only `TinyRateLimitError`, `TinyServerError`, `TinyTimeoutError` should requeue |
| Transport | `TinyClient` does not accept `session` or transport objects |
| Timeout | Always `tuple[float, float]`, never a single float |
| Testing | Mock `HTTPAdapter`, never `requests.Session` directly |

---

## Page map

The skill routes questions to the correct doc page automatically:

| Question type | Page fetched |
|---------------|-------------|
| How to set up the client | `client.md` |
| Exceptions and error handling | `exceptions.md` |
| Rate limits, RPM, multi-process | `rate-limiting.md` |
| Products methods | `resources/products.md` |
| Orders methods | `resources/orders.md` |
| Product model fields | `models/product.md` |
| Order model fields | `models/order.md` |
| FastAPI integration | `guides/fastapi.md` |
| RabbitMQ / Celery workers | `guides/rabbitmq.md` |
| Async usage | `guides/async.md` |
| General / first question | `quickstart.md` |
| What is planned | `roadmap.md` |
