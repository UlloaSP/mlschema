# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
"""Core strict inference API and field contracts for MLschema."""

from mlschema.core.app import (
    FieldBuilder,
    FieldContext,
    FieldDict,
    FieldKind,
    infer_schema,
    kind,
    with_positional_mappings,
)
from mlschema.core.domain import BaseField
from mlschema.core.exceptions import (
    EmptyDataFrameError,
    FieldBuilderError,
    FieldKindAlreadyRegisteredError,
    FieldKindError,
    FieldServiceError,
    InvalidValueError,
    MLSchemaError,
    UnknownFieldKindError,
)

__all__ = [
    "BaseField",
    "EmptyDataFrameError",
    "FieldBuilder",
    "FieldBuilderError",
    "FieldContext",
    "FieldDict",
    "FieldKind",
    "FieldKindAlreadyRegisteredError",
    "FieldKindError",
    "FieldServiceError",
    "InvalidValueError",
    "MLSchemaError",
    "UnknownFieldKindError",
    "infer_schema",
    "kind",
    "with_positional_mappings",
]
