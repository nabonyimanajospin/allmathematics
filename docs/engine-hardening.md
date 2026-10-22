# Math engine hardening

Implemented in Phase 1:

- Hand-written parser, no `eval`, no `sympify` of raw input. Closed grammar, known functions only.
- Limits: 500 characters, nesting depth 40, 400 operations, powers bounded by size in bits.
- Every check runs under an 8-second wall-clock limit and returns a friendly message on timeout.
- Shared secret header on every `/v1` route (`ENGINE_TOKEN`, compared in constant time). `/docs` and `/openapi.json` are disabled.
- The engine refuses to answer if no token is configured.
- Pydantic validation (types, lengths) on every request.

Planned (Phase 2, before the generator and quizzes go live):

- Run SymPy in a pool of worker **processes** so a timed-out job can be killed. Today a timed-out thread keeps
  running until it finishes (it cannot be killed), so the web layer also rate-limits checks (90 per minute per user).
- Per-process memory limit.
- Network policy: the engine accepts connections only from the web backend.
