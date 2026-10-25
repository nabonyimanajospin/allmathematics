# Allmaths

A university-level mathematics learning platform: **Geometry**, **Multivariable Calculus and Differential Equations**, and **Probability and Statistics**.

- Every answer is checked by a real math engine (SymPy), and every value is exact: fractions, radicals, π and e, never rounded decimals.
- A learner follows **one course at a time**, reads lessons with figures and worked examples, solves at least 15 exercises per lesson, takes a test at the end of each unit, and sees a progress percentage that is computed on the server.
- Tools inside the account: a **Solver** (step-by-step answers, no AI), a **Grapher** (2D, 3D, points, segments, exact roots), a personal **formula sheet**, and the **Resources** of the course.
- An **admin panel**: users, statistics, feedback, resources, password resets.

## Run it on your computer (Windows, about 10 minutes)

This is the whole procedure from an empty computer folder, for example after you deleted the project and want it back.
No Docker and no database server are needed: the database runs inside the app.

### 0. What to install once

| Tool | Check in PowerShell | If missing |
|---|---|---|
| Git | `git --version` | https://git-scm.com |
| Node 22 or newer | `node --version` | https://nodejs.org (LTS) |
| pnpm | `pnpm --version` | `npm i -g pnpm` |
| Python 3.11 or newer | `python --version` | https://www.python.org (tick **Add python.exe to PATH**) |

**The first install needs the internet** (about 500 MB of packages: the website's packages with `pnpm`, and SymPy and FastAPI with `pip`). After that, everything works offline.

### 1. Get the project and install it (first time only)

Choose a **short** folder path (for example `C:\allmaths`): Windows fails on very long paths.

```powershell
git clone https://github.com/nabonyimanajospin/allmathematics.git C:\allmaths
cd C:\allmaths
pnpm install
cd apps/math-engine
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements-dev.txt
cd ../..
```

`pnpm install` and `pip install` take a few minutes. Nothing else is needed: the lessons, the exercises and their verified answers are all in the repository, and the database is created by the website on its first start.

### 2. Every time: two PowerShell windows

**Window 1: the math engine** (port 8001)

```powershell
cd apps/math-engine
$env:ENGINE_TOKEN = "dev-engine-token"
.\.venv\Scripts\python -m uvicorn allmaths_engine.main:app --host 127.0.0.1 --port 8001
```

**Window 2: the website** (port 3000), from the project folder

```powershell
$env:MATH_ENGINE_TOKEN = "dev-engine-token"
pnpm dev
```

The two tokens must be the same text. When the website says `Ready`, open **http://localhost:3000**.

**The very first page can take 1 to 2 minutes** (the site reads and prepares all 109 lessons); every page after that is fast. Keep both windows open while you use the site, and close them (Ctrl+C) when you finish.

To check that the engine is alive, open http://127.0.0.1:8001/health in the browser: it must show `{"status":"ok"}`.

### 3. Demo accounts (optional, recommended for a presentation)

Stop the website (Ctrl+C in window 2), then run once:

```powershell
pnpm seed
```

| Account | E-mail | Password |
|---|---|---|
| Learner | `student@allmaths.test` | `demo-password-123` |
| Instructor | `instructor@allmaths.test` | `demo-password-123` |
| Administrator | `admin@allmaths.test` | `demo-password-123` |

Start the website again (`pnpm dev`). You can also click **Create account** and make your own.

### Your own administrator account (without the demo accounts)

Before starting the website, list your e-mail, then sign up with it on the site; that account becomes an administrator:

```powershell
$env:ADMIN_EMAILS = "you@example.com"
pnpm dev
```

See [docs/administration.md](docs/administration.md) for what an administrator can do.

### If something does not work

| Message or problem | What to do |
|---|---|
| `Port 3000 is in use` or `Another next dev server is already running` | The site is already running: open http://localhost:3000. To restart it, close the old PowerShell window (or `taskkill /PID <number> /F` with the number shown in the message), then run `pnpm dev` again. |
| The Solver says "temporarily unavailable" | The math engine (window 1) is not running, or the two tokens differ. |
| `Not enough space on the disk` | Free some space on drive C: (the browser tests and Next.js write temporary files). |
| After an update, new pages show errors | Stop and start **both** windows: the website applies database changes when it starts, and the engine needs its new code. |
| `No module named uvicorn` (or `fastapi`, `sympy`) | The `pip install` step did not finish or was skipped. Run it again from `apps/math-engine`: `.\.venv\Scripts\python -m pip install -r requirements-dev.txt` (needs the internet). |
| `python` or `pnpm` is not recognised | Install it (table in step 0), then close and reopen PowerShell. |
| `The system cannot find the path specified` while installing or starting | The project folder path is too long. Clone into a short folder such as `C:\allmaths`. |
| You want the newest version later | In the project folder: `git pull`, then `pnpm install`, then stop and start both windows. Your accounts and progress stay in the `.data` folder (it is not in Git, so a new clone starts empty; run `pnpm seed` again for the demo accounts). |
| The password reset code does not arrive | Without an e-mail service, the 6-digit code is printed in window 2 (the website's console). |

## How progress is counted

The same explanation is on the site itself (**How is my progress counted?** at the foot of every lesson and of *My learning*, page `/how-progress-works`). Every percentage is computed **on the server** from what the learner really did, with exact fractions (no floating point), and it is rounded **down**, so 100% means that everything is truly done. The browser never sends a percentage.

| Level | How it is counted |
|---|---|
| **Lesson** | Two thirds sections, one third exercises: `(40 × sections credited ÷ all sections + 20 × exercises solved ÷ all exercises) ÷ 60`. A lesson is 100% only when every section is credited and every exercise is solved. |
| **Section** | A reading section (concept, definition, theorem, formula, example, figure, summary) counts after its **minimum active time** (10 to 20 seconds, measured by the server's own clock), so scrolling past it does not count. A check question counts when it is answered correctly. |
| **Exercise** | Counts when the math engine marks the answer correct (any equivalent exact form). Every exercise of the lesson is in the total. |
| **Unit** | 80% the average of its lessons, weighted by their estimated minutes, plus 20% when the unit test is passed (7 correct answers out of 10). |
| **Module** | The average of its units, weighted by minutes. |
| **Course** | The average of its modules, weighted by minutes. |

Example: a lesson with 10 sections and 20 exercises, 8 sections credited and 15 exercises solved: `(40 × 8/10 + 20 × 15/20) ÷ 60 = 47/60`, shown as **78%**.

Because progress is recomputed from the learner's answers every time the dashboard opens, adding sections or exercises to a lesson makes the same work a smaller share; the lesson is complete again once the new items are done. The formulas are in `packages/core/src/progress.ts` (covered by unit tests) and the specification is section 9.2 of `MATH_PLATFORM_BUILD_SPEC.md`. The page on the site takes its numbers (the weights, the minimum seconds and the example) from that same code, so it cannot disagree with the real calculation.

## A tour for a presentation (10 minutes)

1. **Sign in as the learner.** Choose a course (one at a time), open a lesson: sections unlock as you answer; the sidebar shows the whole course and the **unit test** of every unit.
2. **Exercises**: type an answer in a stacked-fraction field; the engine checks it and explains the solution step by step. A hint is available, the percentage updates, and the lesson has a printable sheet.
3. **Unit test**: 10 questions (at most 3 multiple choice), pass mark 7, new questions at every attempt.
4. **Solver** (header): try *derivative of x^2\*sin(x)*, *critical points of x^3 - 3\*x\*y + y^3*, *determinant of [[2,1,0],[1,3,1],[0,1,4]]*, *double integral of x^2 + y^2 in polar coordinates over r from 0 to 2, theta from 0 to 2\*pi*. There is a clickable list of examples.
5. **Grapher** (header): type `y = x^2 - 2` and `y = 2*x - 3`; exact roots and intersections are listed; use the tools to add points, segments and lines; open the 3D tab.
6. **Formula sheet**: save formulas from lessons.
7. **Sign in as the administrator**: statistics, users, feedback from learners, resources, audit log.

## Daily commands

| Command | What it does |
|---|---|
| `pnpm dev` | The website (needs `MATH_ENGINE_TOKEN`) |
| `pnpm typecheck`, `pnpm lint` | Code checks |
| `pnpm test` | Unit and service tests (the math engine must be running) |
| `pnpm test:engine` | The Python engine tests |
| `pnpm verify-content` | Checks every lesson and recomputes **every answer key** with the engine |
| `pnpm seed` | Demo accounts (stop the website first) |

Browser tests (run them in isolation, never against the site you are using; see [docs/running.md](docs/running.md)):

```powershell
$env:E2E_PORT = "3100"; $env:E2E_ENGINE_PORT = "8101"; $env:NEXT_DIST_DIR = ".next-e2e"
$env:PGLITE_DIR = "$env:TEMP\allmaths-e2e-db"
pnpm --filter @allmaths/web exec playwright test
```

## What is inside

```text
apps/web            Next.js app: learners, instructors and administrators
apps/math-engine    FastAPI + SymPy: checks answers, step-by-step solver, exact graph values (internal only)
packages/notation   LaTeX macros for the notation standard, and the notation lint
packages/core       Exact progress formulas, graph mathematics, engine client (pure, shared)
packages/content-schema   Lesson schemas, loader, content verification pipeline
packages/db         PostgreSQL schema (Drizzle) and migrations
packages/server     Business rules: auth, sessions, progress, tests, feedback, admin
packages/ui         Design tokens (light/dark) and shared components
content/            The lessons: Course → Module → Unit → Lesson (YAML), with generated exercises
resources/          Downloadable documents of each course
scripts/            verify-content, seed, content authoring (SymPy builders)
```

## Documentation

- [docs/running.md](docs/running.md): running, updating, browser tests, production notes
- [docs/administration.md](docs/administration.md): the first administrator, users, feedback, announcements, audit log
- [docs/solver-and-premium.md](docs/solver-and-premium.md): what the Solver understands, the free plan, Premium and payment
- [docs/grapher.md](docs/grapher.md): what the Grapher draws and its tools
- [docs/architecture.md](docs/architecture.md), [docs/security.md](docs/security.md): why it is built this way
- [MATH_PLATFORM_BUILD_SPEC.md](MATH_PLATFORM_BUILD_SPEC.md): the specification

## Status

Content: Geometry (modules 1 to 3), Multivariable Calculus and Differential Equations (modules 1 to 5), Probability and Statistics (modules 1 to 3), with at least 15 exercises in every lesson, each with hints and a worked solution.
Not done yet: reading a picture of a handwritten problem, live online payment (needs the owner's payment keys), and the statistics inference module.
