from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field, model_validator
from pydantic_core import PydanticCustomError

from mlschema.core.domain import BaseField
from mlschema.strategies.domain.field_types import FieldTypes


class CategoryField(BaseField):
    type: Literal[FieldTypes.CATEGORY] = FieldTypes.CATEGORY
    value: str | None = None
    options: Annotated[list[str], Field(min_length=1)]

    @model_validator(mode="after")
    def _check_value_in_options(self) -> CategoryField:
        if self.value is not None and self.value not in self.options:
            raise PydanticCustomError(
                "value_error", "Value must match one of the allowed options"
            )
        return self
