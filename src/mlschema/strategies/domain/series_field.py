# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BeforeValidator, Field, PositiveInt, model_validator
from pydantic_core import PydanticCustomError

from mlschema.core.domain import BaseField
from mlschema.strategies.domain.field_types import FieldTypes
from mlschema.strategies.domain.series_column import parse_column

_Column = Annotated[dict[str, Any], BeforeValidator(parse_column)]


class SeriesField(BaseField):
    """Two-axis series with ordered local columns and one parent mapping.

    Columns have ids field1 and field2, scalar-kind properties, and no mappedTo.
    """

    kind: Literal[FieldTypes.SERIES] = FieldTypes.SERIES
    columns: Annotated[list[_Column], Field(min_length=2, max_length=2)]
    minPoints: PositiveInt | None = None
    maxPoints: PositiveInt | None = None

    @model_validator(mode="after")
    def _check_series_constraints(self) -> SeriesField:
        if [column["id"] for column in self.columns] != ["field1", "field2"]:
            raise PydanticCustomError(
                "series_column_order", "Series columns must be field1 then field2"
            )
        if (
            self.minPoints is not None
            and self.maxPoints is not None
            and self.minPoints > self.maxPoints
        ):
            raise PydanticCustomError(
                "series_points_constraint",
                "minPoints ({min_points}) must be ≤ maxPoints ({max_points})",
                {"min_points": self.minPoints, "max_points": self.maxPoints},
            )
        return self
