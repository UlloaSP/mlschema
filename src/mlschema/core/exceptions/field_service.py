# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
"""Input validation errors for field inference."""

from __future__ import annotations

from typing import Any

from ._base import InvalidValueError


class FieldServiceError(InvalidValueError):
    """Base error for invalid runtime inputs supplied to inference.

    Args:
        param: Logical input name that failed validation.
        value: Offending value supplied to the inference API.
        message: Optional human-readable message. A default is generated when
            omitted.
        context: Optional machine-readable diagnostics.

    Attributes:
        param: Name of the failing logical input.
        value: Invalid value.
        context: Optional diagnostics inherited from `MLSchemaError`.
    """

    def __init__(
        self,
        param: str,
        value: Any,
        message: str | None = None,
        *,
        context: dict[str, Any] | None = None,
    ) -> None:
        default = f"Field inference received invalid value for {param!r}: {value!r}."
        super().__init__(param, value, message or default, context=context)
