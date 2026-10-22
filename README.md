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

**Phase 1 (foundation) is complete.** Geometry, Module 1 (Vectors), Unit 1, Lessons 1–3 are live.
Next: Phase 2, assessment and tracking (problem generator, quizzes, mastery, dashboard).
