# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
"""Field-builder output validation errors."""

from __future__ import annotations

from mlschema.core.exceptions.field_kind import FieldKindError


class FieldBuilderError(FieldKindError):
    """Raised when a field builder returns unusable data.

    Examples:
        Builder failures include returning a non-dict value, omitting `kind`,
        referencing missing override columns, or leaving a column unmatched after
        all builders have run.
    """
