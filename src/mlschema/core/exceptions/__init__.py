# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
"""Public exception hierarchy for MLSchema.

All package-specific exceptions derive from `MLSchemaError`. Leaf errors are
split by responsibility so callers can catch broad domains (`FieldKindError`,
`FieldServiceError`) or specific failures (`UnknownFieldKindError`).
"""

from mlschema.core.exceptions._base import InvalidValueError, MLSchemaError
from mlschema.core.exceptions.empty_dataframe import EmptyDataFrameError
from mlschema.core.exceptions.field_builder import FieldBuilderError
from mlschema.core.exceptions.field_kind import FieldKindError
from mlschema.core.exceptions.field_kind_conflict import FieldKindAlreadyRegisteredError
from mlschema.core.exceptions.field_service import FieldServiceError
from mlschema.core.exceptions.unknown_field_kind import UnknownFieldKindError

__all__ = [
    "EmptyDataFrameError",
    "FieldBuilderError",
    "FieldKindAlreadyRegisteredError",
    "FieldKindError",
    "FieldServiceError",
    "InvalidValueError",
    "MLSchemaError",
    "UnknownFieldKindError",
]
