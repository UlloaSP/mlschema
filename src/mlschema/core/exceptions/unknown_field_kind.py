# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
"""Unknown generated field-kind errors."""

from __future__ import annotations

from mlschema.core.exceptions.field_kind import FieldKindError


class UnknownFieldKindError(FieldKindError):
    """Raised when a builder emits an unregistered field kind.

    Args:
        kind_name: Field-kind discriminator found in builder output.

    Attributes:
        param: Always `"kind"`.
        value: Unknown kind name.
        context: Contains `{"offender": kind_name}`.
    """

    def __init__(self, kind_name: str) -> None:
        super().__init__(
            param="kind",
            value=kind_name,
            message=f'Field kind "{kind_name}" is not registered.',
            context={"offender": kind_name},
        )
