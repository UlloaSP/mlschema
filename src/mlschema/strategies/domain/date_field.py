# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
from __future__ import annotations

from typing import Literal

from pydantic import PositiveInt, model_validator
from pydantic_core import PydanticCustomError

from mlschema.core.domain import BaseField
from mlschema.strategies.domain.field_types import FieldTypes


class DateField(BaseField):
    kind: Literal[FieldTypes.DATE] = FieldTypes.DATE
    defaultValue: str | None = None
    min: str | None = None
    max: str | None = None
    step: PositiveInt | None = None

    @model_validator(mode="after")
    def _check_dates(self) -> DateField:
        # ISO date strings (YYYY-MM-DD) sort lexicographically, so string comparison is valid.
        if self.min is not None and self.max is not None and self.min > self.max:
            raise PydanticCustomError(
                "date_range_error",
                "Minimum date must be earlier than or equal to maximum date",
            )

        if self.defaultValue is not None:
            if self.min is not None and self.defaultValue < self.min:
                raise PydanticCustomError(
                    "date_min_error",
                    "defaultValue must be later than or equal to minimum date",
                )
            if self.max is not None and self.defaultValue > self.max:
                raise PydanticCustomError(
                    "date_max_error",
                    "defaultValue must be earlier than or equal to maximum date",
                )
        return self
