# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
"""Errors raised while registering strict field kinds."""

from __future__ import annotations

from typing import Any

from mlschema.core.exceptions._base import InvalidValueError


class FieldKindError(InvalidValueError):
    """Base error for invalid field-kind definitions.

    Args:
        param: Logical argument or field name that failed validation.
        value: Offending value supplied by the caller.
        message: Optional human-readable message. A default is generated when
            omitted.
        context: Optional machine-readable diagnostics.

    Attributes:
        param: Name of the failing logical parameter.
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
        default = f"Invalid field kind value for {param!r}: {value!r}."
        super().__init__(param, value, message or default, context=context)
