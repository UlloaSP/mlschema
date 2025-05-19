from typing import Annotated
from pydantic import Field, model_validator

from mlschema.domain.fields import BaseField, FieldTypes


class TextField(BaseField):
    type: Annotated[FieldTypes, Field(const=True)] = FieldTypes.TEXT
    value: str | None = None
    placeholder: str | None = None
    minLength: int | None = None
    maxLength: int | None = None
    pattern: str | None = Field(
        default=None,
        description="Expresión regular en notación Python; "
        "Pydantic no conserva instancias de re.Pattern en JSON‐serialización.",
    )

    @model_validator(mode="after")
    def _check_lengths(self) -> "TextField":
        if (
            self.minLength is not None
            and self.maxLength is not None
            and self.minLength > self.maxLength
        ):
            raise ValueError(
                f"minLength ({self.minLength}) debe ser ≤ maxLength ({self.maxLength})"
            )
        return self
