# Instructions for AI assistants and new contributors

This repository is **Allmaths**, a mathematics learning platform (secondary school to doctorate). Whatever tool you are, the rules are the same:

1. Read [`CLAUDE.md`](CLAUDE.md) (the working rules and commands) and [`docs/standards/README.md`](docs/standards/README.md) (the global standards) **before** changing content or code.
2. The non-negotiable rules: every answer verified by the math engine (`apps/math-engine`); exact values only; the notation of `packages/notation` and [`docs/standards/notation-and-naming.md`](docs/standards/notation-and-naming.md); progress computed on the server; correct answers never sent to the browser before an attempt; every feature with tests.
3. Every lesson follows the one template of [`docs/standards/curriculum-structure.md`](docs/standards/curriculum-structure.md); never invent a new order, a new name for an existing thing, or a new notation for one lesson.
4. No AI in the learner-facing mathematics: the solver, the answer checking and the grapher are rule-based and verified.
5. "Rule" in the standards applies now; "Proposed" waits for the owner's confirmation; "Target" is not built yet. Never present a target as done; report test results as they are.
6. Commits are small, with plain messages, authored by the repository owner only (no co-author lines).
7. Never write LaTeX through a shell heredoc or a non-raw string: use an editor tool (a backslash before r, t, n or f becomes a control character).
