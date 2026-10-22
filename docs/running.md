# Running Allmaths on your computer

You need: **Node 22+** (24 is used), **pnpm** (`npm i -g pnpm`), **Python 3.11+**, **Git**.
No Docker and no database server are needed: development uses PGlite, a real PostgreSQL that runs inside Node
and stores its files in `.data/pglite`.

## First time

```powershell
pnpm install
cd apps/math-engine
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements-dev.txt
cd ../..
```

## Every day (two terminals)

**Terminal 1: the math engine** (internal service, port 8001)

```powershell
cd apps/math-engine
$env:ENGINE_TOKEN = "dev-engine-token"
.\.venv\Scripts\python -m uvicorn allmaths_engine.main:app --host 127.0.0.1 --port 8001
```

**Terminal 2: the website** (port 3000)

```powershell
$env:MATH_ENGINE_TOKEN = "dev-engine-token"
pnpm dev
```

Open <http://localhost:3000>, click **Create account**, and open Lesson 1.

### Demo users (optional)

Stop the website first (PGlite allows one process at a time), then:

```powershell
pnpm seed
```

This creates `student@allmaths.test`, `instructor@allmaths.test`, `admin@allmaths.test`
(password `demo-password-123`). It refuses to run in production.

## Checks

| Command | What it does |
|---|---|
| `pnpm typecheck` | TypeScript strict, all packages |
| `pnpm lint` | ESLint (no `any`) |
| `pnpm test` | Unit and service tests (the math engine must be running, they use it) |
| `pnpm test:engine` | Python engine tests (run from the venv) |
| `pnpm verify-content` | Content pipeline: schema, KaTeX, notation lint, **every result recomputed by the engine** |
| `pnpm verify-content -- --static` | Same without the engine |
| `pnpm --filter @allmaths/web exec playwright test` | Browser tests (desktop and phone), including accessibility |

Engine tests: `cd apps/math-engine; .\.venv\Scripts\python -m pytest`

## Writing a lesson

Content lives in `content/<course>/<module>/<unit>/<lesson>/lesson.yaml`. Copy an existing lesson, edit it,
then run `pnpm verify-content`. The command tells you the exact section and rule for every problem.
The dev server reloads content when a file changes.

## Production notes

Set `DATABASE_URL` (PostgreSQL), `MATH_ENGINE_URL`, `MATH_ENGINE_TOKEN` (long random string, same as the engine's
`ENGINE_TOKEN`), and keep the engine on a private network. The app refuses to start in production without them.
