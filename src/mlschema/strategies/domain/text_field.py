from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator
from pydantic_core import PydanticCustomError

from mlschema.core.domain import BaseField
from mlschema.strategies.domain.field_types import FieldTypes


class TextField(BaseField):
    type: Literal[FieldTypes.TEXT] = FieldTypes.TEXT
    value: str | None = None
    placeholder: str | None = None
    minLength: int | None = None
    maxLength: int | None = None
    pattern: str | None = Field(
        default=None,
        description=(
            "Regular expression in Python notation; Pydantic does not preserve "
            "re.Pattern instances in JSON serialization."
        ),
    )

    @model_validator(mode="after")
    def _check_lengths(self) -> TextField:
        if (
            self.minLength is not None
            and self.maxLength is not None
            and self.minLength > self.maxLength
        ):
            raise PydanticCustomError(
                "length_validation",
                "minLength ({min_length}) must be ≤ maxLength ({max_length})",
                {"min_length": self.minLength, "max_length": self.maxLength},
            )

        if (
            self.value is not None
            and self.minLength is not None
            and len(self.value) < self.minLength
        ):
            raise PydanticCustomError(
                "min_length_validation",
                "value length ({value_length}) must be ≥ minLength ({min_length})",
                {"value_length": len(self.value), "min_length": self.minLength},
            )

        if (
            self.value is not None
            and self.maxLength is not None
            and len(self.value) > self.maxLength
        ):
            raise PydanticCustomError(
                "max_length_validation",
                "value length ({value_length}) must be ≤ maxLength ({max_length})",
                {"value_length": len(self.value), "max_length": self.maxLength},
            )

        return self
