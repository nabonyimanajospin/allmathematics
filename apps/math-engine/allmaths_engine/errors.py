"""Errors raised by the engine. Every error carries a stable code and a message that is safe to show to a student."""

from __future__ import annotations


class EngineError(ValueError):
    """Base class. `code` is stable (used by the UI for i18n), `message` is English fallback text."""

    code = "engine_error"

    def __init__(self, message: str, code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code


class ParseError(EngineError):
    """The input is not valid math in the supported syntax."""

    code = "parse_error"


class ComplexityError(EngineError):
    """The input is valid but too large or too complex to process safely."""

    code = "too_complex"
