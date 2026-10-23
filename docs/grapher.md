# The grapher

A page (`/graph`, for signed-in learners: it is part of the account) for plotting, in the browser, with no library: the mathematics is in `packages/core/src/graph.ts` and
uses the same safe evaluator as the lesson plots (no `eval`).

## 2D

One line per object, up to eight, each with its own colour. What you type decides what is drawn:

| Type | Example |
|---|---|
| function of x | `y = x^2 - 3`, `sin(x)/x`, `2x(x+1)` |
| x as a function of y | `x = y^2` |
| implicit curve | `x^2 + y^2 = 9`, `x*y = 1` (drawn by marching squares) |
| polar | `r = 1 + cos(theta)` |
| parametric | `(cos(t), sin(t))`, `(t, t^2), t in [0, 3]` |
| point (named) | `A(2, 3)` or `A = (2, 3)`; a capital letter, so `f(x)` stays a function |
| segment, line | `segment(A, B)`, `line(A, B)` through two named points |
| inequality (shaded) | `y > x^2`, `x^2 + y^2 <= 4` (dashed border for `<` and `>`) |

Implicit multiplication works (`2x`, `x(x+1)`, `ax^2+bx+c`). Any single letter that is not `x`, `y`, `t` or a constant becomes a **slider**
(from −10 to 10), so `y = a*x^2 + b` gives two sliders and the curve moves as they move. A function is broken where it is undefined or jumps over an
asymptote (`tan(x)`, `1/x`).

Drag to pan, wheel or pinch to zoom, arrow keys and `+`/`−` from the keyboard, `Home` to reset; the coordinates under the cursor are shown.

## 3D

A surface `z = f(x, y)` (shaded by height, or as a wireframe) and an optional space curve `(x(t), y(t), z(t)), t in [a, b]`, with sliders for
parameters. Drag to rotate, wheel to zoom, arrow keys from the keyboard. The grid is 36 × 36 and the surface is drawn back to front.

## Tools (like a geometry program)

Above the picture: **Move**, **Point**, **Segment**, **Line**.

- **Point**: touch the picture; a point is added on the nearest half grid step and named A, B, C, ... (a new line `A = (x, y)` appears).
- **Segment** / **Line**: touch one point, then another (touching an empty place makes a new point); a line `segment(A, B)` / `line(A, B)` is added.
- **Move**: drag the picture, or drag a point (the segments that use it follow). Escape cancels a half-made segment.
- **Measurements** under the picture: for every segment its exact length (`√13`, `3√2/2`), midpoint and the equation of the line through the two points,
  as exact fractions when the coordinates are decimals with at most 3 digits; otherwise marked ≈.
- The dots where lines meet are small, so that they do not hide the picture.

## Roots, intersections and sharing

Under the picture the grapher lists where a line `y = f(x)` crosses the x-axis and where two such lines meet. The browser first finds them numerically
(bisection); then the math engine (`/v1/graph/exact`, SymPy) makes each one exact when it can prove the value: it lists every real solution when it can, or
recognises the value as a rational multiple of pi, a radical or e and accepts the guess only if it satisfies the equation exactly. So `x^2 - 2` gives
`(\sqrt2, 0)` and `sin(x)` gives `(\pi, 0)`. A value with no closed form (`cos(x) = x`) stays a decimal marked with ≈. Sliders are sent as exact fractions.
**Copy link** puts the expressions in the address (`#g=...`), so whoever opens the
link sees the same graph. Nothing is stored on the server.

## Not included (yet)

Geometric constructions (points that move along lines), parametric surfaces, intersections with curves that are not of the form `y = f(x)`.
