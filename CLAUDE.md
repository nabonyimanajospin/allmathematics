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
- Never write LaTeX through a shell heredoc (``, `	`, `
` become control characters); use the editor tools.
- A format hint of an exercise set must not contain the answer of one of its exercises (verify-content checks this).
- Commits: small, plain messages, authored by the repository owner only (no co-author lines).

## Current phase
Phase 1 foundation done; Course 1 (geo) Modules 2 and 3 written, Module 1 Unit 2 (products) and Module 2 polar coordinates and conics still to write; Course 2 (mvc) Modules 1 to 4 written (PDE module still to write).
Spec version 1.2 (hierarchy: Course > Module > Unit > Lesson).
