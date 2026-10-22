# Security notes (spec section 13)

| Requirement | State |
|---|---|
| Passwords hashed | scrypt (N=32768, r=8, p=1), random salt per user, parameters stored with the hash, constant-time compare. |
| Sessions | Random 256-bit token, only its SHA-256 is stored; HTTP-only, SameSite=Lax, Secure in production; 30 days sliding; killed when the account is suspended. |
| CSRF | SameSite=Lax cookies **and** every state-changing request must carry a same-origin `Origin` (or `Sec-Fetch-Site: same-origin`). |
| Sign-in does not reveal accounts | Same message and similar time for unknown e-mail, wrong password, suspended account. |
| Rate limiting | Sign-in (per IP and per e-mail), sign-up, answer checks, hints, events. In-memory today (Redis later). |
| Role checks on the server | `can(role, permission)` in `@allmaths/server`; roles cannot be chosen at sign-up. |
| Answer keys | Never sent to the browser. Verified by a unit test over all lessons and a browser test. |
| Input validation | Zod on every route; request bodies limited to 32 KB; ids restricted to `[a-z0-9-]`. |
| Math input | Safe parser; see `engine-hardening.md`. |
| Headers | CSP (inline scripts still allowed, nonce planned), `X-Frame-Options: DENY`, `nosniff`, `Referrer-Policy`, `Permissions-Policy`, HSTS in production. |
| Logs | Unknown errors are logged server-side with a stack trace and shown to users as a generic message. No personal data is logged by the app itself. |

To do before launch: e-mail verification, password reset, account export and deletion, encrypted backups, audit log writes
for admin actions, payment webhook signature verification.
