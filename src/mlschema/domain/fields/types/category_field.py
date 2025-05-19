from typing import Annotated, List, Union
from pydantic import Field, model_validator

from mlschema.domain.fields import BaseField, FieldTypes


class CategoryField(BaseField):
    type: Annotated[FieldTypes, Field(const=True)] = FieldTypes.CATEGORY
    value: str | int | None = None
    options: Annotated[List[Union[str, int]], Field(min_length=1)]

    @model_validator(mode="after")
    def _check_value_in_options(self) -> "CategoryField":
        if self.value is not None and self.value not in self.options:
            raise ValueError(
                "El valor debe coincidir con una de las opciones permitidas"
            )
        return self
