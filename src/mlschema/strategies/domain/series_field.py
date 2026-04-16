# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BeforeValidator, PositiveInt, SerializeAsAny, model_validator
from pydantic_core import PydanticCustomError

from mlschema.core.domain import BaseField
from mlschema.strategies.domain.boolean_field import BooleanField
from mlschema.strategies.domain.category_field import CategoryField
from mlschema.strategies.domain.date_field import DateField
from mlschema.strategies.domain.field_types import FieldTypes
from mlschema.strategies.domain.number_field import NumberField
from mlschema.strategies.domain.text_field import TextField

# Module-level registry: type_name → field class
# Pre-populated with 5 built-ins; extend via add_series_sub_field()
_SUB_FIELD_REGISTRY: dict[str, type[BaseField]] = {
    FieldTypes.BOOLEAN: BooleanField,
    FieldTypes.CATEGORY: CategoryField,
    FieldTypes.DATE: DateField,
    FieldTypes.NUMBER: NumberField,
    FieldTypes.TEXT: TextField,
}


def add_series_sub_field(cls: type[BaseField]) -> None:
    """Register a custom BaseField subclass as valid SeriesField sub-field.

    Raises ValueError if cls has type == "series" (no nesting allowed).
    """
    type_val = str(cls.model_fields["type"].default)
    if type_val == FieldTypes.SERIES:
        raise ValueError("SeriesField cannot be registered as a sub-field (no nesting)")
    _SUB_FIELD_REGISTRY[type_val] = cls


def _parse_sub_field(v: Any) -> BaseField:
    """BeforeValidator: resolve dict → concrete BaseField subclass via registry."""
    if isinstance(v, BaseField):
        if v.__class__.__name__ == "SeriesField":
            raise PydanticCustomError(
                "no_series_nesting", "SeriesField cannot be nested"
            )
        return v
    if isinstance(v, dict):
        type_name = str(v.get("type", ""))
        if type_name == FieldTypes.SERIES:
            raise PydanticCustomError(
                "no_series_nesting", "SeriesField cannot be nested"
            )
        cls = _SUB_FIELD_REGISTRY.get(type_name)
        if cls is None:
            raise PydanticCustomError(
                "unknown_sub_field_type",
                "Unknown sub-field type: '{type_name}'. Register via add_series_sub_field().",
                {"type_name": type_name},
            )
        return cls(**v)
    raise PydanticCustomError(
        "invalid_sub_field", "Sub-field must be a dict or BaseField instance"
    )


_SubField = Annotated[SerializeAsAny[BaseField], BeforeValidator(_parse_sub_field)]


class SeriesField(BaseField):
    """Field schema for a series (two-axis) column.

    Attributes:
        type:       Fixed type identifier ``"series"``.
        field1:     Schema of the first element of each cell.
        field2:     Schema of the second element of each cell.
        min_points: Minimum number of data points in the series (≥ 1).
        max_points: Maximum number of data points in the series (≥ 1).
    """

    type: Literal[FieldTypes.SERIES] = FieldTypes.SERIES
    field1: _SubField
    field2: _SubField
    min_points: PositiveInt | None = None
    max_points: PositiveInt | None = None

    @model_validator(mode="after")
    def _check_series_constraints(self) -> SeriesField:
        if (
            self.min_points is not None
            and self.max_points is not None
            and self.min_points > self.max_points
        ):
            raise PydanticCustomError(
                "series_points_constraint",
                "min_points ({min_points}) must be ≤ max_points ({max_points})",
                {"min_points": self.min_points, "max_points": self.max_points},
            )
        return self
