# The grapher

A page (`/graph`, open to everyone) for plotting, in the browser, with no library: the mathematics is in `packages/core/src/graph.ts` and
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
| point | `(2, 3)` |

Implicit multiplication works (`2x`, `x(x+1)`, `ax^2+bx+c`). Any single letter that is not `x`, `y`, `t` or a constant becomes a **slider**
(from −10 to 10), so `y = a*x^2 + b` gives two sliders and the curve moves as they move. A function is broken where it is undefined or jumps over an
asymptote (`tan(x)`, `1/x`).

Drag to pan, wheel or pinch to zoom, arrow keys and `+`/`−` from the keyboard, `Home` to reset; the coordinates under the cursor are shown.

## 3D

A surface `z = f(x, y)` (shaded by height, or as a wireframe) and an optional space curve `(x(t), y(t), z(t)), t in [a, b]`, with sliders for
parameters. Drag to rotate, wheel to zoom, arrow keys from the keyboard. The grid is 36 × 36 and the surface is drawn back to front.

## Not included (yet)

Geometric constructions (points that move along lines, intersections of objects), inequalities with shading, parametric surfaces, saving a graph.
These are what makes GeoGebra a complete geometry tool; the grapher is the function-and-surface part of it.
