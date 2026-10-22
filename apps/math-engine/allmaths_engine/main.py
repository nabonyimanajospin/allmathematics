"""Internal HTTP API of the math engine. Never expose this service publicly (spec section 13).

Every /v1 endpoint requires the shared secret in the X-Engine-Token header.
"""

from __future__ import annotations

import hmac
import os
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from . import checker
from . import ode as ode_mod
from .errors import EngineError

MAX_TEXT = 500


def _expected_token() -> str:
    token = os.environ.get("ENGINE_TOKEN", "")
    if len(token) < 8:
        # Refuse to run open. Tests and dev set ENGINE_TOKEN explicitly.
        raise HTTPException(status_code=503, detail="Engine is not configured.")
    return token


def require_token(x_engine_token: Annotated[str | None, Header()] = None) -> None:
    expected = _expected_token()
    if x_engine_token is None or not hmac.compare_digest(x_engine_token.encode(), expected.encode()):
        raise HTTPException(status_code=401, detail="Unauthorized.")


app = FastAPI(title="Allmaths math engine", version="0.1.0", docs_url=None, redoc_url=None, openapi_url=None)


class MistakeIn(BaseModel):
    expr: str = Field(max_length=MAX_TEXT)
    hint: str = Field(max_length=300)


class ConstraintIn(BaseModel):
    equation: str = Field(max_length=MAX_TEXT)
    solve_for: str = Field(pattern=r"^[A-Za-z]$")
    ranges: dict[str, tuple[float, float]] = Field(default_factory=dict, max_length=4)


class ConditionIn(BaseModel):
    at: str = Field(max_length=60)
    value: str = Field(max_length=60)
    derivative: int = Field(default=0, ge=0, le=2)


class OdeIn(BaseModel):
    order: int = Field(ge=1, le=3)
    equation: str | None = Field(default=None, max_length=MAX_TEXT)
    family: str | None = Field(default=None, max_length=MAX_TEXT)
    constants: list[str] = Field(default_factory=list, max_length=4)
    conditions: list[ConditionIn] = Field(default_factory=list, max_length=3)
    sample: tuple[float, float] = (0.6, 1.9)


class CheckRequest(BaseModel):
    answer_type: Literal[
        "number", "expression", "vector", "point", "multiple_choice", "auto",
        "region", "equation", "direction", "points", "ode_solution", "ode_family",
    ]
    student: str = Field(max_length=MAX_TEXT)
    correct: str = Field(max_length=MAX_TEXT)
    input_format: Literal["auto", "latex", "text"] = "auto"
    variables: list[str] | None = Field(default=None, max_length=10)
    allow_decimal: bool = False
    sig_figs: int | None = Field(default=None, ge=1, le=10)
    mistakes: list[MistakeIn] = Field(default_factory=list, max_length=10)
    coordinates: list[str] | None = Field(default=None, max_length=4)
    constraint: ConstraintIn | None = None
    ode: OdeIn | None = None


class CheckResponse(BaseModel):
    status: Literal["correct", "incorrect", "invalid"]
    code: str
    message: str
    student_latex: str | None = None
    method: str | None = None
    parts: list[bool] | None = None
    hint: str | None = None


class ComputeRequest(BaseModel):
    expression: str = Field(max_length=MAX_TEXT)


class ComputeResponse(BaseModel):
    ok: bool
    text: str | None = None
    latex: str | None = None
    code: str | None = None
    message: str | None = None


class VerifyRequest(BaseModel):
    a: str = Field(max_length=MAX_TEXT)
    b: str = Field(max_length=MAX_TEXT)


class VerifyResponse(BaseModel):
    equal: bool
    method: str | None = None
    code: str | None = None
    message: str | None = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/check", response_model=CheckResponse, dependencies=[Depends(require_token)])
def check(req: CheckRequest) -> CheckResponse:
    result = checker.check_answer(
        answer_type=req.answer_type,
        student=req.student,
        correct=req.correct,
        input_format=req.input_format,
        variables=req.variables,
        allow_decimal=req.allow_decimal,
        sig_figs=req.sig_figs,
        mistakes=[checker.Mistake(m.expr, m.hint) for m in req.mistakes],
        coordinates=req.coordinates,
        constraint=(
            checker.Constraint(req.constraint.equation, req.constraint.solve_for, dict(req.constraint.ranges))
            if req.constraint
            else None
        ),
        ode=(
            ode_mod.OdeSpec(
                order=req.ode.order,
                equation=req.ode.equation,
                family=req.ode.family,
                constants=req.ode.constants,
                conditions=[ode_mod.Condition(c.at, c.value, c.derivative) for c in req.ode.conditions],
                sample=req.ode.sample,
            )
            if req.ode
            else None
        ),
    )
    return CheckResponse(
        status=result.status,
        code=result.code,
        message=result.message,
        student_latex=result.student_latex,
        method=result.method,
        parts=result.parts,
        hint=result.hint,
    )


@app.post("/v1/compute", response_model=ComputeResponse, dependencies=[Depends(require_token)])
def compute(req: ComputeRequest) -> ComputeResponse:
    try:
        text, latex = checker.compute(req.expression)
    except EngineError as exc:
        return ComputeResponse(ok=False, code=exc.code, message=exc.message)
    return ComputeResponse(ok=True, text=text, latex=latex)


@app.post("/v1/verify", response_model=VerifyResponse, dependencies=[Depends(require_token)])
def verify(req: VerifyRequest) -> VerifyResponse:
    try:
        equal, method = checker.values_equal(req.a, req.b)
    except EngineError as exc:
        return VerifyResponse(equal=False, code=exc.code, message=exc.message)
    return VerifyResponse(equal=equal, method=method)
