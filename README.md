# CodeSage AI

CodeSage AI is a full-stack GitHub pull-request review platform. It prepares a bounded, diff-first context, coordinates specialist AI reviews, validates structured findings, derives transparent code-health scores, and presents the results in a polished developer dashboard.

It is designed as a portfolio-quality MVP: **Demo Mode works without external credentials**, while the production integration boundaries for GitHub OAuth/App tokens, signed webhooks, PostgreSQL, and OpenAI are in the API.

## Architecture

```mermaid
flowchart TD
  U[Developer] --> W[Next.js / React dashboard]
  W --> A[FastAPI API]
  A --> P[(PostgreSQL)]
  A --> G[GitHub OAuth + App API]
  G --> H[Signed pull_request webhook]
  H --> A
  A --> C[Diff context builder]
  C --> O[Review orchestrator]
  O --> S[Security agent]
  O --> B[Bug agent]
  O --> F[Performance agent]
  O --> M[Maintainability agent]
  O --> T[Testing agent]
  O --> R[Structured Pydantic findings + scorer]
```

## What is implemented

- Dark-first responsive Next.js SaaS UI: landing page, dashboard, repositories, PR review, diff preview, review history, review detail, and settings.
- Demo Mode with visibly labelled realistic repositories, PRs, findings, analytics, score cards, generated fixes/tests, and contextual chat.
- FastAPI REST API with OpenAPI docs at `/docs` and useful loading/error/empty states in the client.
- Async SQLAlchemy models and Alembic initial migration for users, GitHub installations, repositories, PRs, reviews, issues, webhook deliveries, and repository settings.
- GitHub OAuth callback with state-cookie protection and signed session cookie; GitHub App JWT/token service; signature-verified, idempotent webhook endpoint.
- Diff-first context filtering that excludes binary/unsupported, lock, generated, minified, and oversized files and reports partial coverage.
- Five specialist review roles coordinated concurrently with the official OpenAI Python SDK structured Pydantic parsing. The dependency list also includes the OpenAI Agents SDK for a future tool-bearing specialist upgrade.
- Deterministic scoring: each review begins at 100; critical/high/medium/low findings deduct 30/15/7/3 points respectively. Category scores apply the same method to category findings and scores clamp at zero.

## Layout

```
apps/
  web/                 Next.js frontend
  api/                 FastAPI backend, agents, services, models, tests
    alembic/           database migration configuration
```

## Local setup

Prerequisites: Node.js 20+, Python 3.11+, and Docker/PostgreSQL only for non-demo development.

```powershell
Copy-Item .env.example .env
cd apps/api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

In a second terminal:

```powershell
cd apps/web
npm install
npm run dev
```

Open `http://localhost:3000`. With `DEMO_MODE=true` the landing demo, dashboard, repository routes, pull request flow, AI-report interaction, review history, and settings all work without secrets.

## Database migrations

For local demo SQLite, tables are created automatically on API startup. For PostgreSQL, first start the local database:

```powershell
docker compose up -d postgres
cd apps/api
.\.venv\Scripts\Activate.ps1
alembic upgrade head
```

Set `DATABASE_URL=postgresql+asyncpg://codesage:codesage@localhost:5432/codesage`. Alembic automatically uses a synchronous driver form when applying the migration.

## Environment variables

See [`.env.example`](.env.example). Required for a full live integration:

- `DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS`, `APP_URL`, `NEXT_PUBLIC_API_URL`
- `OPENAI_API_KEY`, `OPENAI_MODEL`
- `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`
- `GITHUB_APP_ID`, `GITHUB_APP_PRIVATE_KEY`, `GITHUB_WEBHOOK_SECRET`
- `DEMO_MODE=false`

Never place the OpenAI key or GitHub App private key in the browser environment. For a one-line private key value, encode PEM newlines as `\n`.

## GitHub App configuration

1. Create a GitHub App from GitHub developer settings.
2. Set the callback URL to `https://YOUR_API/api/auth/github/callback` and the webhook URL to `https://YOUR_API/webhooks/github`.
3. Generate a private key and place it only in `GITHUB_APP_PRIVATE_KEY`.
4. Subscribe to the **Pull request** webhook event.
5. Use minimum permissions: **Metadata: read-only**, **Contents: read-only**, **Pull requests: read-only** for retrieval. Add **Pull requests: read/write** only if enabling explicit summary/inline publishing, and never enable auto-publishing by default.
6. Install the App on selected repositories. Store installation IDs server-side; mint short-lived installation tokens per API operation.

The webhook handler rejects unsigned or invalid signatures and stores GitHub delivery IDs so duplicate deliveries are idempotent. It evaluates `opened`, `reopened`, and `synchronize` pull request actions. In production, attach the review execution service to a durable worker/queue adapter before handling significant traffic; the service boundary is intentionally independent from the HTTP view layer.

## First real PR test

1. Set the production variables and turn `DEMO_MODE=false`.
2. Run migrations and the API/frontend.
3. Install the GitHub App on a test repository.
4. Open a PR containing a small TypeScript/Python source change.
5. Trigger `POST /api/repositories/{owner}/{repo}/pulls/{number}/review` from the PR view (or send a signed `pull_request.opened` webhook).
6. Confirm the stored review reaches `completed`, check `/api/reviews/{id}`, then explicitly use **Publish to GitHub** after granting write permission.

## API surface

- `GET /health`, `GET /api/auth/me`, `GET /api/auth/github`, `GET /api/auth/github/callback`
- `GET /api/repositories`, `GET /api/repositories/{owner}/{repo}`, `GET /api/repositories/{owner}/{repo}/pulls`, `GET /api/repositories/{owner}/{repo}/pulls/{number}`
- `POST /api/repositories/{owner}/{repo}/pulls/{number}/review`
- `GET /api/reviews`, `GET /api/reviews/{id}`, `POST /api/reviews/{id}/publish`
- `POST /api/reviews/{id}/issues/{issue}/fix`, `POST /api/reviews/{id}/issues/{issue}/test`, `POST /api/reviews/{id}/chat`
- `GET /api/dashboard`, `POST /webhooks/github`

## Quality checks

```powershell
cd apps/api
ruff check .
pytest

cd ../web
npm run typecheck
npm run build
```

## Deployment notes

- Deploy `apps/web` to Vercel with `NEXT_PUBLIC_API_URL` set to the public API origin.
- Deploy `apps/api` to Render, Railway, or Fly.io with a managed PostgreSQL URL.
- Set precise HTTPS CORS origins, a long random `SECRET_KEY`, secure cookies, GitHub OAuth callback/webhook URLs, and production `APP_URL`.
- Run `alembic upgrade head` as a deployment release command. Use a managed queue such as Redis/Celery, Dramatiq, or an equivalent worker adapter for high-volume asynchronous reviews.

## Resume description

**Concise version**

- Built CodeSage AI, a GitHub pull-request review platform with Next.js, FastAPI, PostgreSQL, and OpenAI structured outputs to identify security, reliability, performance, maintainability, and testing risks.
- Designed a secure GitHub App/webhook architecture with diff-first context limiting, Pydantic-validated findings, deterministic health scoring, and a production-style review dashboard.

**Detailed version**

Built an AI-powered GitHub code-review platform using Next.js, FastAPI, PostgreSQL, and specialist-agent orchestration. The system processes bounded pull-request diffs, validates structured security/bug/performance/maintainability/testing findings, derives transparent scores in application code, persists review history, and supports GitHub App authentication plus signature-verified webhook automation without exposing external credentials to the browser.
