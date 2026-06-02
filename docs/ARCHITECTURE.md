# Architecture

This document describes the runtime architecture of **TestForge AI**, the
moving parts, and the contracts between them.

## High-level diagram

```
                         ┌──────────────────────────┐
                         │      Browser (UI)        │
                         │  Next.js 15 / React 19   │
                         └─────────────┬────────────┘
                                       │ HTTPS
                                       │  /api/generate, /api/history
                                       ▼
                ┌────────────────────────────────────────────────┐
                │                FastAPI backend                 │
                │                                                │
                │   routes.py  →  test_case_service.py           │
                │                      │                         │
                │        ┌─────────────┼──────────────┐          │
                │        │             │              │          │
                │        ▼             ▼              ▼          │
                │  cache.py   gemini_service   pdf_service       │
                │  (LRU+TTL)  (google-genai)  (ReportLab)        │
                │        │             │              │          │
                └────────┼─────────────┼──────────────┼──────────┘
                         │             │              │
                         │             │              │
                  ┌──────▼──────┐ ┌────▼─────┐  ┌─────▼──────┐
                  │ PostgreSQL  │ │  Gemini  │  │   PDF      │
                  │  (history)  │ │   API    │  │  bytes     │
                  └─────────────┘ └──────────┘  └────────────┘
```

## Components

| Layer       | Module                                | Responsibility                                            |
|-------------|---------------------------------------|-----------------------------------------------------------|
| Frontend    | `app/`                                | Pages (home, generator, results, history)                 |
| Frontend    | `components/`                         | UI building blocks (cards, buttons, sections, etc.)       |
| Frontend    | `services/api.ts`                     | Typed client for the backend HTTP API                     |
| Frontend    | `lib/hooks/`                          | Reusable React hooks (debounce, localStorage)             |
| Frontend    | `lib/format.ts`                       | Pure functions (Markdown serialisation, text formatters)  |
| Backend     | `api/routes.py`                       | HTTP endpoints and OpenAPI metadata                       |
| Backend     | `services/test_case_service.py`       | Orchestrates Gemini + cache + persistence                 |
| Backend     | `services/gemini_service.py`          | Thin wrapper around `google-genai` with retries + parsing |
| Backend     | `services/cache.py`                   | In-process LRU+TTL cache for repeated requirements        |
| Backend     | `services/pdf_service.py`             | ReportLab-based PDF renderer                              |
| Backend     | `database/session.py`                 | SQLAlchemy engine, session factory, `get_db` dependency   |
| Backend     | `models/test_generation.py`           | ORM model for the `test_generations` table                |
| Backend     | `schemas/test_case.py`                | Pydantic request/response models                          |
| Backend     | `middleware/request_id.py`            | Adds an `X-Request-ID` header to every response           |
| Backend     | `middleware/errors.py`                | Uniform JSON error responses                              |
| Backend     | `migrations/` (Alembic)               | Versioned schema migrations                               |
| Backend     | `scripts/cli.py`                      | CLI for ad-hoc generation and PDF export                  |
| Backend     | `scripts/smoke_test.py`               | End-to-end smoke test with a stubbed Gemini client        |
| Backend     | `tests/`                              | Pytest unit tests                                         |

## Data flow — generate flow

1. User submits the form on `/generate`.
2. The Next.js client calls `POST /api/generate` with the requirement.
3. FastAPI validates the body with `GenerateRequest`.
4. `TestCaseService.generate_and_store` is invoked.
5. The service checks the in-process cache. On miss it calls Gemini with
   retries and a strict JSON-only system prompt.
6. The response is normalised and validated against `TestCase`.
7. The result is stored in PostgreSQL and returned to the client.
8. The client navigates to `/results?id=<id>` which renders the cards.

## Data flow — history

- `GET /api/history` returns lightweight summaries (id, requirement,
  timestamp, test-case count) — newest first.
- `GET /api/history/{id}` returns the full generation including the
  test cases.
- `GET /api/history/{id}/pdf` streams a PDF render of a single
  generation.

## Error handling

A uniform error shape is produced by `backend/middleware/errors.py`:

```json
{
  "detail": "Human-readable message",
  "error_id": "abc123...",
  "errors": [/* only on 422 */]
}
```

`error_id` is the same value as the `X-Request-ID` response header so
operators can grep logs for a failing request.

## Persistence

Schema lives in `backend/migrations/` and is managed by Alembic.
For green-field local development, `init_db()` (called on app
startup) creates tables using `Base.metadata.create_all` as a
convenience. Production deployments should rely on the migration
files instead:

```bash
python -m alembic upgrade head
```

## Deployment considerations

* The backend is stateless except for the optional in-process cache;
  scale horizontally by running multiple workers behind a load
  balancer. Replace the in-process cache with Redis if you need a
  shared cache.
* The PDF endpoint is a pure CPU/IO path; it can be served from the
  same process without a worker queue.
* The frontend is a standard Next.js app; deploy to Vercel, Netlify,
  or any Node-capable host.
* Set `LOG_JSON=1` in production to emit structured logs.

## Extensibility hooks

* **Swap the model.** Set `GEMINI_MODEL=gemini-1.5-pro` in `.env`.
* **Auth.** The API has no authentication today. Add a FastAPI
  dependency that resolves the current user and scope queries by
  user id.
* **CI integration.** `formatAllTestCasesAsMarkdown` is a pure
  function — import it from a small script to push test plans into
  Jira or a wiki on each PR.
