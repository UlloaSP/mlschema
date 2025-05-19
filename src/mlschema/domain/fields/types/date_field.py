from datetime import date
from typing import Annotated
from pydantic import Field, PositiveInt, model_validator

from mlschema.domain.fields import BaseField, FieldTypes


class DateField(BaseField):
    type: Annotated[FieldTypes, Field(const=True)] = FieldTypes.DATE
    value: date | None = None
    min: date | None = None
    max: date | None = None
    step: PositiveInt = 1  # días de salto

    @model_validator(mode="after")
    def _check_dates(self) -> "DateField":
        if self.min and self.max and self.min > self.max:
            raise ValueError(
                "La fecha mínima debe ser anterior o igual a la fecha máxima"
            )

        if self.value:
            if self.min and self.value < self.min:
                raise ValueError(
                    "La fecha debe ser posterior o igual a la fecha mínima"
                )
            if self.max and self.value > self.max:
                raise ValueError("La fecha debe ser anterior o igual a la fecha máxima")
        return self
