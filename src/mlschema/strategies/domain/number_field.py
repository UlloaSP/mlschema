# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
from __future__ import annotations

from typing import Literal

from pydantic import model_validator
from pydantic_core import PydanticCustomError

from mlschema.core.domain import BaseField
from mlschema.strategies.domain.field_types import FieldTypes


class NumberField(BaseField):
    kind: Literal[FieldTypes.NUMBER] = FieldTypes.NUMBER
    defaultValue: float | int | None = None
    min: float | None = None
    max: float | None = None
    step: float | None = 1
    placeholder: str | None = None
    unit: str | None = None

    @model_validator(mode="after")
    def _check_numeric_constraints(self) -> NumberField:
        if self.min is not None and self.max is not None and self.min > self.max:
            raise PydanticCustomError(
                "min_max_constraint",
                "min ({min}) must be ≤ max ({max})",
                {"min": self.min, "max": self.max},
            )

        if self.defaultValue is not None:
            if self.min is not None and self.defaultValue < self.min:
                raise PydanticCustomError(
                    "value_min_constraint",
                    "defaultValue ({value}) must be ≥ min ({min})",
                    {"value": self.defaultValue, "min": self.min},
                )
            if self.max is not None and self.defaultValue > self.max:
                raise PydanticCustomError(
                    "value_max_constraint",
                    "defaultValue ({value}) must be ≤ max ({max})",
                    {"value": self.defaultValue, "max": self.max},
                )
        return self
