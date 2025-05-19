from typing import Annotated, Union

from mlschema.domain.fields.types import (
    BooleanField,
    CategoryField,
    DateField,
    NumberField,
    TextField,
)
from pydantic import Field


FieldUnion = Annotated[
    Union[
        NumberField,
        TextField,
        BooleanField,
        DateField,
        CategoryField,
    ],
    Field(discriminator="type"),
]
