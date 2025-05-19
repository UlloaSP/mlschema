from typing import Annotated
from pydantic import Field

from mlschema.domain.fields import BaseField, FieldTypes


class BooleanField(BaseField):
    type: Annotated[FieldTypes, Field(const=True)] = FieldTypes.BOOLEAN
    value: bool | None = None
