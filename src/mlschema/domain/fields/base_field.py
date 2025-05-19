from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field


class BaseField(BaseModel):
    """Metadatos estándar de cualquier campo."""

    model_config = ConfigDict(extra="forbid", frozen=False)

    title: Annotated[str, Field(min_length=1, max_length=100)]
    description: Annotated[str | None, Field(max_length=500)] = None
    required: bool = True
