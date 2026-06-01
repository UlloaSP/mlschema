# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
"""Duplicate field-kind registration errors."""

from __future__ import annotations

from mlschema.core.exceptions.field_kind import FieldKindError


class FieldKindAlreadyRegisteredError(FieldKindError):
    """Raised when two field kinds use the same kind name.

    Args:
        kind_name: Duplicate field-kind discriminator.

    Attributes:
        param: Always `"kind"`.
        value: The duplicate kind name.
        context: Contains `{"offender": kind_name}`.
    """

    def __init__(self, kind_name: str) -> None:
        super().__init__(
            param="kind",
            value=kind_name,
            message=f'Field kind "{kind_name}" is already registered.',
            context={"offender": kind_name},
        )
