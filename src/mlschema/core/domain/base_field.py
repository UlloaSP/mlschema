from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class BaseField(BaseModel):
    """Standard metadata present in **all** fields.

    Extend this class to define custom field types.

    Attributes:
        title: Human-readable field identifier (1-100 characters).
        description: Optional description (max. 500 characters).
        required: True if the original column contains no null values.
    """

    model_config = ConfigDict(extra="forbid", frozen=False)

    title: Annotated[str, Field(min_length=1, max_length=100)]
    description: Annotated[str | None, Field(max_length=500)] = None
    required: bool = True
