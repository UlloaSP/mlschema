from __future__ import annotations

from typing import Literal

from pydantic import model_validator
from pydantic_core import PydanticCustomError

from mlschema.core.domain import BaseField
from mlschema.strategies.domain.field_types import FieldTypes


class NumberField(BaseField):
    type: Literal[FieldTypes.NUMBER] = FieldTypes.NUMBER
    min: float | None = None
    max: float | None = None
    step: float | None = 1
    placeholder: str | None = None
    value: float | None = None
    unit: str | None = None

    @model_validator(mode="after")
    def _check_numeric_constraints(self) -> NumberField:
        if self.min is not None and self.max is not None and self.min > self.max:
            raise PydanticCustomError(
                "min_max_constraint",
                "min ({min}) must be ≤ max ({max})",
                {"min": self.min, "max": self.max},
            )

        if self.value is not None:
            if self.min is not None and self.value < self.min:
                raise PydanticCustomError(
                    "value_min_constraint",
                    "value ({value}) must be ≥ min ({min})",
                    {"value": self.value, "min": self.min},
                )
            if self.max is not None and self.value > self.max:
                raise PydanticCustomError(
                    "value_max_constraint",
                    "value ({value}) must be ≤ max ({max})",
                    {"value": self.value, "max": self.max},
                )
        return self
