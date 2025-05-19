"""Summary"""

from typing import Annotated, List
from mlschema.domain.fields import FieldUnion
from pydantic import BaseModel, ConfigDict, Field


class Form(BaseModel):
    model_config = ConfigDict(extra="forbid")

    input: Annotated[List[FieldUnion], Field(min_length=1)]
