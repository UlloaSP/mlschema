from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import PositiveInt, model_validator
from pydantic_core import PydanticCustomError

from mlschema.core.domain import BaseField
from mlschema.strategies.domain.field_types import FieldTypes


class DateField(BaseField):
    type: Literal[FieldTypes.DATE] = FieldTypes.DATE
    value: date | None = None
    min: date | None = None
    max: date | None = None
    step: PositiveInt = 1

    @model_validator(mode="after")
    def _check_dates(self) -> DateField:
        if self.min and self.max and self.min > self.max:
            raise PydanticCustomError(
                "date_range_error",
                "Minimum date must be earlier than or equal to maximum date",
            )

        if self.value:
            if self.min and self.value < self.min:
                raise PydanticCustomError(
                    "date_min_error", "Date must be later than or equal to minimum date"
                )
            if self.max and self.value > self.max:
                raise PydanticCustomError(
                    "date_max_error",
                    "Date must be earlier than or equal to maximum date",
                )
        return self
