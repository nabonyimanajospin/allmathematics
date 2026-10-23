# Allmaths

A university-level mathematics learning platform: geometry, multivariable calculus, differential equations.
Every answer is checked by a real math engine, all values are exact (no decimals), and progress is tracked
section by section on the server.

- **Specification:** [MATH_PLATFORM_BUILD_SPEC.md](MATH_PLATFORM_BUILD_SPEC.md) (the single source of truth)
- **Run it:** [docs/running.md](docs/running.md)
- **Why it is built this way:** [docs/architecture.md](docs/architecture.md), [docs/security.md](docs/security.md)

## Structure

```text
apps/web            Next.js app (students; instructor and admin screens come later)
apps/math-engine    FastAPI + SymPy: checks answers, verifies content (internal only)
packages/notation   LaTeX macros for the notation standard, and the notation lint
packages/core       Exact progress formulas, event schema, engine client (pure, shared)
packages/content-schema   Lesson schemas, loader, content verification pipeline
packages/db         PostgreSQL schema (Drizzle) and migrations
packages/server     Business rules: auth, sessions, events, progress, answer checks
packages/ui         Design tokens (light/dark) and shared components
content/            The lessons: Course → Module → Unit → Lesson (YAML)
scripts/            verify-content, seed
```

## Status

**Phase 1 (foundation) is complete.** Content so far:

- Geometry: Module 1 (vectors, products), Module 2 (the line with its eight equations, the triangle with all its centers, cevians
  and circles, the circle, polar coordinates and curves, conics and loci), Module 3 (lines and planes in space, the tetrahedron,
  the sphere, quadric surfaces).
- Multivariable Calculus and Differential Equations: derivatives, double and triple integrals, ordinary differential equations,
  partial differential equations (characteristics, heat, wave and Laplace equations, Fourier series).
- Probability and Statistics: counting, probability and Bayes, random variables, data and the least-squares line.
- 92 lessons with several hundred exercises, each with hints and a worked solution. Every answer key is recomputed by the math
  engine in `pnpm verify-content`.

The platform also has: a Resources page with downloadable course documents, a personal formula sheet, an answer field that writes
fractions stacked as in print, and 2D and rotatable 3D figures drawn from exact coordinates.

Next: Phase 2, assessment and tracking (problem generator, quizzes, mastery, dashboard).






























You run it as two programs in two terminals: the math engine, then the website. This is from [docs/running.md](docs/running.md). I haven't run it myself.

**You need:** Node 22+, pnpm (`npm i -g pnpm`), Python 3.11+ and Git. You don't need Docker or a database server.

**First time only** (from the project root):
```powershell
pnpm install
cd apps/math-engine
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements-dev.txt
cd ../..
```

**Every time:**

Terminal 1 starts the math engine on port 8001:
```powershell
cd apps/math-engine
$env:ENGINE_TOKEN = "dev-engine-token"
.\.venv\Scripts\python -m uvicorn allmaths_engine.main:app --host 127.0.0.1 --port 8001
```

Terminal 2 starts the website on port 3000:
```powershell
$env:MATH_ENGINE_TOKEN = "dev-engine-token"
pnpm dev
```

The two tokens must be the same string.

Then open http://localhost:3000, click **Create account**, and open Lesson 1.

**Optional demo users:** stop the website first, because the database allows only one process at a time. Then run `pnpm seed`. It creates `student@allmaths.test`, `instructor@allmaths.test` and `admin@allmaths.test`, all with the password `demo-password-123`.

**Checks:** `pnpm typecheck`, `pnpm lint`, `pnpm test` (the engine must be running), `pnpm test:engine` and `pnpm verify-content`.