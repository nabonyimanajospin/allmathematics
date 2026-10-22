# Architecture decisions (Phase 1)

| Decision | Why |
|---|---|
| **Course → Module → Unit → Lesson** hierarchy | Owner's curriculum; ids `geo-m01-u01-l01` are stable and readable. |
| **pnpm monorepo**, packages consumed as TypeScript source | No build step between packages; one `typecheck` for everything. |
| **PGlite in development, PostgreSQL in production** (Drizzle ORM) | Zero install for the owner; same SQL and migrations everywhere. |
| **`@allmaths/server` holds the business rules** | Auth, progress, events, checks live in one tested place, not in routes or components. |
| **`@allmaths/core`** (not in the original structure) | Pure, dependency-free logic shared by browser and server: exact progress formulas, event schema, engine client. |
| **Lessons are `lesson.yaml`, not MDX** | Strict, line-accurate schema errors; no code execution in content; the future editor writes the same JSON. |
| **Own session auth** (scrypt, hashed session tokens, HTTP-only cookies) | No third-party fee or beta dependency; Google sign-in can be added next to it. |
| **Progress is computed from stored facts with exact fractions (bigint)** | `1/14` is stored as `1/14`; 100% is shown only when exactly complete. |
| **The server credits reading time** | A client may claim time, but never more than the server clock allows; the same elapsed time cannot be claimed twice. |
| **Only 4 event verbs come from the browser** | `started`, `viewed`, `resumed`, `bookmarked`. Answers, hints and passes are recorded by the server itself. |
| **Answer keys never leave the server** | Lessons are sent through `toClientLesson`; a test and an e2e check prove no key, hint or explanation is in the page. |

## Progress when a lesson has no practice or quiz yet

The formula `0.40·sections + 0.20·practice + 0.40·quiz` is applied to the components a lesson *has*.
Phase 1 lessons have only sections, so their weight is renormalised and a fully read lesson shows 100%.
In Phase 2 each lesson gains practice and a quiz and the full formula applies automatically
(`lessons.has_practice`, `lessons.has_quiz`).

## Deliberate Phase 1 limits (tracked)

- Email verification, password reset and Google sign-in: Phase 5 (before payments).
- MathLive visual keyboard: Phase 2. Phase 1 uses a text field with a symbol bar; the engine already accepts the LaTeX MathLive produces.
- Rate limiting is in-memory (one process). A Redis implementation replaces it behind the same interface.
- Content-Security-Policy still allows inline scripts (Next.js); a nonce-based policy is planned.
- The engine limits work with timeouts in threads; process isolation is planned (see `engine-hardening.md`).
