# The public site

The lecturer's requirement: **a very simple and very professional public structure**, which explains how the platform works, how progress is tracked and what is inside, with a small, discreet credit of the people who built it.

## 1. Pages (Target)

| Page | Address | Purpose and content | Today |
|---|---|---|---|
| Home | `/` | One sentence on what Allmaths is; the courses with their levels; one button to start; three short facts (exact answers checked by a math engine, notes and tests for everything, progress you can trust) | exists, to simplify |
| What is inside | `/courses` (public view) | Every course → module → unit, with level, number of lessons, exercises and tests; what each lesson contains (notes, figures, worked examples, quick checks, exercises with worked solutions, final answers, unit tests) | course choice exists for signed-in learners; public catalog to build |
| How it works | `/how-it-works` | The learning path in five steps: read the lesson, follow the worked examples, answer the quick checks, solve the exercises, pass the unit test; the tools (solver, grapher, triangle toolkit, formula sheet, resources); how answers are checked (exact values, the math engine, no AI) | to build |
| How progress is counted | `/how-progress-works` | The exact formulas, with an example (built from the code that computes progress) | exists |
| Team | `/team` | Small page, linked discreetly from the footer: each person's **name, title and role** (for example "Lecturer, Mathematics; content review"), in a plain list | to build (names to be given by the owner) |
| Feedback | `/feedback` | Report a problem or a mistake | exists (signed-in) |
| Privacy and terms | `/privacy`, `/terms` | Required before a public launch | to write |

Rules:

- The header has **few links** (for a signed-in learner: My learning, Formula sheet, Grapher, Solver, Resources). New tools go inside an existing page (the triangle toolkit is a tab of the Solver), not into the header.
- The footer carries the small links: How it works, How progress is counted, Team, Feedback, Privacy, Terms, and the copyright line.
- No marketing exaggeration; every claim on the site is true today.

## 2. Visual design (Rule)

- **One design system**: the tokens of `packages/ui` (colors, spacing, radius, shadows, typography) for every page; no page-specific colors or sizes.
- Light and dark themes; the light theme is the default for every first visit, whatever the computer's setting; white page background for lessons in the light theme.
- Typography: one font family for text, KaTeX for mathematics; headings in sentence case; line length about 70 characters for reading.
- Components are reused (Card, Button, Field, ProgressBar); a new pattern is added to `packages/ui` before it is used twice.
- Motion only to explain a change, and none when the learner prefers reduced motion.

## 3. Accessibility and performance (Rule)

- WCAG 2.2 level AA: contrast, keyboard use, labels for every field, visible focus, no information by color alone; mathematics readable by screen readers (KaTeX MathML).
- Every page works on a phone 360 px wide without sideways scrolling.
- Fast on a slow connection: server-rendered pages, mathematics rendered on the server, no large libraries loaded on pages that do not need them.
- Automated checks: the browser tests run an accessibility scan on every main page.
