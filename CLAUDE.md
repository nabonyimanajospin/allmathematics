# CLAUDE.md

## Project
University-level math learning platform (vectors, analytic geometry,
multivariable calculus, differential equations). Full spec:
MATH_PLATFORM_BUILD_SPEC.md. Read it before any large change.

## Non-negotiable rules
1. Mathematical correctness first. Every answer is verified by the math
   engine (apps/math-engine). Never hard-code an answer you did not verify.
2. Exact values only: fractions, simplified radicals, symbolic π and e.
   No decimals unless the question explicitly asks for an approximation.
3. Notation from packages/notation only:
   vectors \vec{u}; dot \dotp{\vec u}{\vec v} -> <u,v>;
   cross \crossp{\vec u}{\vec v} -> [u,v];
   box \boxp{\vec u}{\vec v}{\vec w} -> <u,v,w>.
4. Progress and scores are computed on the server from events.
5. Correct answers are never sent to the client before submission.
6. Every feature ships with tests. CI must be green.

## Structure of content
Course -> Module -> Unit -> Lesson -> Section (spec section 2.1).
Courses: geo (Geometry), mvc (Multivariable Calculus and DE), stat (later).
Ids look like geo-m01-u01-l01. The owner's notes folder is reference only;
write original content (spec section 12.2).

## Commands
- Install: `pnpm install` (Python engine: see docs/running.md)
- Engine: `cd apps/math-engine; .venv\Scripts\python -m uvicorn allmaths_engine.main:app --port 8001` (needs ENGINE_TOKEN)
- Web: `pnpm dev` (needs MATH_ENGINE_TOKEN; PGlite database in .data/, no Docker)
- Checks: `pnpm typecheck`, `pnpm lint`, `pnpm test`, `pnpm test:engine`, `pnpm verify-content`
- Browser tests: `pnpm --filter @allmaths/web exec playwright test`
- Demo users: stop the web server, then `pnpm seed`
- Full guide: docs/running.md. Decisions: docs/architecture.md. Security: docs/security.md

## Conventions
- TypeScript strict, no any. Zod for validation.
- Database changes only via migrations.
- UI strings through i18n.
- Respect prefers-reduced-motion.

## Authoring content
- Lessons are `lesson.yaml`; exercises of a lesson are in a sibling `exercises.yaml` (generated, do not edit by hand).
- Exercise keys are computed with SymPy by the builders in `scripts/authoring/` (run `build_all.py [module]` with the
  engine's Python, then `fix_dfrac.py`, then `pnpm verify-content` with the engine running).
- The printed exercise sheet (MATH126, T. Hakizimana) is fully inside course mvc; printed errors are corrected and shown
  in the exercise `note`.
- Never write LaTeX through a shell heredoc or a Python string that is not raw (a backslash before r, t, n or f becomes a control character, and a replace whose
  pattern does not match silently does nothing); use the editor tools.
- A format hint of an exercise set must not contain the answer of one of its exercises (verify-content checks this).
- Notation in lessons: a vector value is written as a column and a point as a row (the renderer turns `\overrightarrow{AB}=(3,4)` into a column
  automatically); a length is `\norm{\overrightarrow{BC}}`, never `BC` alone (`a=\norm{\overrightarrow{BC}}`); the area of a triangle is `S`.
  Parametric equations use `\begin{cases}`; the vector equation of a line is a point plus lambda times a column vector.
- Units: lengths in lu, areas in squ, volumes in cu. Geometry builders switch this on with `@with_units`.
- Figures: a `visual` section with `kind: figure` and a `figure:` block (2D or rotatable 3D, exact coordinates, see `packages/core/src/figure.ts`).
  Plot legends (`l1`..`l5`) are LaTeX. Put the key formula of a lesson before its first question (questions lock what follows).
- Resources (downloadable documents) are listed in `resources/resources.yaml`; only `permission: granted` files can be downloaded.
- Every lesson must have at least 15 exercises, and a lesson is 100% only when all its sections are read and all its exercises are solved (spec 9.2, v1.3).
  Extra practice is added by the `more_*.py` modules in `scripts/authoring/` (registered in `build_all.py`, merged by `toolkit.write_exercises`); every key is computed
  with SymPy and cross-checked numerically. After any build run `fix_dfrac.py`; it also rewrites `a/b` inside `$...$` of lessons, so never write `(3,3)/(3\sqrt2)` there.
- A student follows one course at a time (enrollments); progress is recomputed from the student's answers on every dashboard load (`refreshProgress`), so content changes never leave a stale percentage.
- Commits: small, plain messages, authored by the repository owner only (no co-author lines).

## Current phase
Phase 1 foundation done. Content written and verified (97 lessons): Course 1 (geo) Modules 1 to 3 (vectors and products, plane with triangle, circle, polar coordinates, conics and loci; space with tetrahedron, sphere, quadric surfaces); Course 2 (mvc) Modules 1 to 5 (including ODE and PDE with Fourier series); Course 3 (stat) Modules 1 to 3 (counting, probability, random variables, data and regression). Also built: resources page (signed-in only), formula sheet (save formulas and theorems from lessons), stacked-fraction answer field, figures in many geometry lessons.
Added since: admin panel (users, stats, resource upload, Premium grants), forgot-password by e-mail code, one-course-at-a-time enrollment, printable lesson sheet, unit tests (10 typed questions, pass 7; a unit is 100% only after passing), progress recomputed from the student's answers, the step-by-step solver (`apps/math-engine/allmaths_engine/solver`, no AI; free 5 per day, Premium unlimited; see docs/solver-and-premium.md), Flutterwave payment code (tested with a simulated provider only), the grapher (/graph, docs/grapher.md), new MVC lessons from the lecture notes, and at least 15 exercises in every lesson.
Not done: photo input for the solver (needs OCR), live payments (needs the owner's Flutterwave keys), geometric constructions in the grapher.
Browser tests: run them in isolation, never against the dev server on port 3000: `E2E_PORT=3100 E2E_ENGINE_PORT=8101 NEXT_DIST_DIR=.next-e2e PGLITE_DIR=<some empty folder> pnpm --filter @allmaths/web exec playwright test` (one run at a time).
Next: Phase 2 (problem generator, quizzes, mastery, dashboard), figures for the remaining lessons, more `more`/`why` explanations, stat inference module.
Spec version 1.4 (every exercise counts for a lesson, the unit test; hierarchy: Course > Module > Unit > Lesson).
