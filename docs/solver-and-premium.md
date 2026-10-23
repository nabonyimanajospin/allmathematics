# The solver, Premium and payments

## What the solver is

A **rule-based** solver. There is no artificial intelligence in it: the typed problem is read with a closed grammar (the same safe parser as the
answer checker), solved with SymPy, explained step by step, and **checked before it is shown**.

| Problem | How it is solved | How it is checked |
|---|---|---|
| Derivative (also 2nd, 3rd) | own step engine: sum, constant multiple, product, quotient, power, chain, exponential rules | compared with SymPy's derivative; never shown if they differ |
| Indefinite and definite integral | SymPy's rule-based integrator (substitution, by parts, standard forms) | the answer is differentiated and must give the integrand; a definite value is also compared with numerical integration |
| Limit | direct substitution, then L'Hôpital for 0/0 | second method plus numeric evaluation near the point |
| Equation, system | linear, factoring, quadratic formula (with the discriminant), higher degree; 2–3 equations | every solution is put back in the equation |
| Ordinary differential equation | type recognised (separable, linear, Bernoulli, exact, homogeneous, constant coefficients), initial conditions | the solution is substituted into the equation |
| Simplify, expand, factor | SymPy | compared at several values |
| Vectors | dot, cross, norm, angle, projection, box product | the cross product is checked orthogonal to both vectors |

When the engine cannot read or cannot verify a problem it **says so** instead of guessing. A word such as "for" is never read as a product of
variables (that bug was found and fixed: `solve x^2=2x for x` returns both solutions). Input is limited to 300 characters.

Every solve runs in a **separate worker process with a time limit** (15 s). A stuck computation is killed and replaced, so it can never block
the website or other learners (`apps/math-engine/allmaths_engine/solver_pool.py`, tested).

## What it cannot do (yet)

* Photographs and handwriting. Reading an image needs optical character recognition for mathematics, which is a trained neural network
  (open source such as pix2tex, or a paid service such as Mathpix). It is not a chatbot, but it is machine learning, and it needs a provider
  or a model on the server. The plan is: the learner uploads a photo, the recognised formula appears **in an editable box**, and only the
  confirmed text is solved, so a misread symbol never produces a silent wrong answer.
* Word problems, proofs, inequalities, integrals that have no elementary antiderivative (the answer says so; some are given with a special
  function such as Si(x) and are still verified).
* PDEs.

## Plans

| | Free | Premium |
|---|---|---|
| Lessons, exercises, unit tests, grapher | yes | yes |
| Solver | 5 successful solves per rolling 24 hours (`SOLVER_FREE_PER_DAY`) | no limit |

A problem the engine cannot read or solve does not use up a solve.

**An administrator gives Premium by hand** in Admin → Users (30, 90 or 365 days, or remove it). Every grant and removal is in the audit log.

## Taking payments (Flutterwave)

The code in `packages/server/src/payments/flutterwave.ts` implements the flow, **tested only against a simulated Flutterwave**
(`packages/server/tests/payments.test.ts`). Test it in Flutterwave's test mode with your own account before real money.

1. Set in the environment of the web server: `FLW_SECRET_KEY`, `FLW_SECRET_HASH` (a random string you also enter in the Flutterwave dashboard
   as the webhook secret hash), `PREMIUM_PRICE` (for example `3000`), `PREMIUM_CURRENCY` (for example `RWF`).
2. In the Flutterwave dashboard set the webhook URL to `https://<your site>/api/payments/webhook`.
3. A learner who reaches the limit sees "Pay for Premium". The server stores a **pending** payment with its own reference and sends the learner
   to Flutterwave (card or MTN/Airtel mobile money in Rwanda).
4. Flutterwave calls the webhook. The call is refused unless it carries the secret hash. The server then asks Flutterwave itself to confirm
   the transaction and checks the reference, the amount, the currency and the status. Only then Premium is granted, **once**, even if the webhook
   is delivered several times.

Nothing is trusted from the browser. Without these settings the payment button is not shown and an administrator can still grant Premium.

## Reading a picture

The solver page has **Read from a picture**. The text is read in the learner's browser with Tesseract (tesseract.js); the picture is never sent to our server,
and the language data is downloaded by the browser the first time. Printed text works best (clear, one problem, good light); handwriting and very small
print are often misread. The recognised text is only a draft: it is put in the problem box for the learner to check and correct before pressing Solve, and
the math engine verifies the answer as always. Signs such as × ÷ − √ π are converted to the typed form, and several lines become a system.

## Messages

Anything the engine cannot read as a problem (an empty box, an unknown word, a missing side of an equation, wrong vectors) is shown as **Check the input.**
with the specific reason below it.
