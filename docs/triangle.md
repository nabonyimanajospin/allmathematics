# The triangle toolkit

Page `/triangle` (signed-in learners, like the Grapher). The learner types the three vertices and gets, **exactly** (fractions, radicals and π; never a decimal):

- the three sides, the longest and the shortest, the perimeter, the semiperimeter and the area, and the kind of triangle (by sides and by angles);
- the three angles (cosine, exact angle, and degrees when the angle is a rational multiple of π);
- the centers **G**, **I**, **O**, **H** and the nine-point center, the radii `r` and `R`, and the Euler line;
- the incircle, the circumcircle and the nine-point circle: center, radius, canonical equation, analytic implicit equation, parametric equations, perimeter and area;
- the three excircles (center and radius);
- fifteen lines (the three sides, medians, altitudes, angle bisectors and perpendicular bisectors), each with its **length** and its **eight equations**: vector, parametric, symmetric (canonical), implicit, explicit, normal (Hesse), polar and intercept form;
- a figure with the triangle, the circles, the centers and the Euler line.

A decimal typed by the learner (`0.5`) is read as the exact fraction (`1/2`). Numbers go up to 10000 with a denominator up to 1000. Three collinear points are refused with an explanation.

## How it is built

| Part | Where |
|---|---|
| The mathematics (SymPy, exact) | `apps/math-engine/allmaths_engine/triangle.py`, endpoint `POST /v1/geometry/triangle` in `main.py` |
| The contract engine ↔ website | Zod schema in `packages/core/src/triangle.ts` (`engine.triangle(points)` in `engine-client.ts`) |
| Rendering of every formula to KaTeX on the server | `apps/web/src/server/triangle.ts`, route `apps/web/src/app/api/triangle/route.ts` |
| The page | `apps/web/src/app/triangle/page.tsx`, `apps/web/src/components/triangle-tool.tsx`, texts in `i18n/en.json` (`triangle.*`) |

The notation follows the course: vectors as columns, fractions as `\dfrac`, equations without empty terms (no `0x`, no `+-`). The Hesse normal form of an angle bisector needs a radical of a radical, so it is shown as the equation divided by `\sqrt{a^2+b^2}` instead of being expanded.

## Tests

- `apps/math-engine/tests/test_triangle.py`: the 3-4-5 triangle, the triangle of the notes, input validation, `HG = 2GO` and `OI² = R² − 2Rr` on five triangles, every line passes through its two points in its implicit, explicit and normal form, lengths of the lines, no decimals.
- `packages/core/tests/triangle.test.ts` and `apps/web/tests/triangle-dto.test.ts`: the contract, with real engine answers in `packages/core/tests/fixtures/` (regenerate them with `analyze()` when the format changes).
- `apps/web/e2e/triangle.spec.ts`: access control, exact values on screen, decimal input, errors, accessibility and the phone layout.

## Extending it

The same pattern (an engine function, an endpoint, a Zod contract, a server rendering step, a page) fits other geometry tools: the tetrahedron (edges, faces, volume, altitudes, circumsphere), a line or plane toolkit, conic sections.
