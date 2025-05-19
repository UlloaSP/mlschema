from typing import Annotated
from pydantic import Field, model_validator

from mlschema.domain.fields import BaseField, FieldTypes


class NumberField(BaseField):
    type: Annotated[FieldTypes, Field(const=True)] = FieldTypes.NUMBER
    min: float | None = None
    max: float | None = None
    step: float | None = None
    placeholder: str | None = None
    value: float | None = None
    unit: str | None = None

    @model_validator(mode="after")
    def _check_numeric_constraints(self) -> "NumberField":
        if self.min is not None and self.max is not None and self.min > self.max:
            raise ValueError(f"min ({self.min}) debe ser ≤ max ({self.max})")

        if self.value is not None:
            if self.min is not None and self.value < self.min:
                raise ValueError(f"value ({self.value}) debe ser ≥ min ({self.min})")
            if self.max is not None and self.value > self.max:
                raise ValueError(f"value ({self.value}) debe ser ≤ max ({self.max})")
        return self
