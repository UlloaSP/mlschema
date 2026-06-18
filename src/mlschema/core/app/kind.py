# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
"""Strict field-kind contracts for MLSchema.

This module defines the public extension types used by `infer_schema()`.
Applications normally customize inference by writing a `FieldBuilder` callable,
and register new field kinds by passing that callable plus a Pydantic
`BaseField` subclass to `kind()`.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pandas import Series
from pydantic import BaseModel

from mlschema.core.domain import BaseField
from mlschema.core.exceptions import FieldKindError

type FieldDict = dict[str, Any]
type MappedToTarget = str | int
type FieldBuilder = Callable[[Series, "FieldContext"], FieldDict | None]
type FieldInfer = Callable[[Series], FieldDict]


@dataclass(frozen=True)
class FieldContext:
    """Column metadata passed to field builders.

    Attributes:
        name: Column name converted to a string for stable JSON labels.
        dtype: Normalised pandas dtype name for the source series.
        required: `True` when the source series contains no null values.
        index: Zero-based column position in the input DataFrame.
        mappedTo: Backend feature name or original model input position.
        infer_field: Recursive callback for builders that need to infer
            sub-fields, such as the builtin series builder.
    """

    name: str
    dtype: str
    required: bool
    index: int
    mappedTo: MappedToTarget
    infer_field: FieldInfer


@dataclass(frozen=True)
class FieldKind:
    """Strict field-kind definition.

    Attributes:
        name: Field discriminator extracted from the model's `kind` default.
        model: Pydantic model used to validate and serialise generated fields.
        infer: Builder callable that can emit fields for this kind.
    """

    name: str
    model: type[BaseField]
    infer: FieldBuilder


def kind(*, model: type[BaseField], infer: FieldBuilder) -> FieldKind:
    """Create a strict field kind from a model and builder.

    Args:
        model: Pydantic field model. It must inherit from `BaseField` and define
            a `kind` field with a concrete default value.
        infer: Callable that receives a pandas `Series` plus `FieldContext`, and
            returns a field dict or `None`.

    Returns:
        Immutable `FieldKind` whose name is derived from `model.kind`.

    Raises:
        FieldKindError: If `model` is not a `BaseField` subclass, does not define
            `kind`, or has a `None` kind default.
    """
    if not issubclass(model, BaseField):
        raise FieldKindError(
            "model",
            model,
            "Field kind model must inherit from BaseField.",
        )
    return FieldKind(name=_kind_name_from_model(model), model=model, infer=infer)


def _kind_name_from_model(model: type[BaseModel]) -> str:
    """Extract a field-kind name from a Pydantic model.

    Args:
        model: Pydantic model expected to expose `model_fields["kind"]`.

    Returns:
        String discriminator used to register and validate field output.

    Raises:
        FieldKindError: If the model does not expose a valid `kind` default.
    """
    field = model.model_fields.get("kind")
    if field is None:
        raise FieldKindError("model", model, "Field kind model must define 'kind'.")
    default = field.default
    if default is None:
        raise FieldKindError("kind", default, "Field kind default cannot be None.")
    return str(default)
