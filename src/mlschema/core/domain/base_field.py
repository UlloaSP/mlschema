# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
from __future__ import annotations

from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field

type MappedToTarget = Annotated[str, Field(min_length=1)] | Annotated[int, Field(ge=0)]


class BaseField(BaseModel):
    """Standard metadata present in **all** fields.

    Aligns with mlform's ``BaseFieldConfig``.  Extend this class to define
    custom field types.

    Attributes:
        label:                     Human-readable field identifier (1-100 chars).
        description:               Optional help text (max 500 chars).
        required:                  Field is mandatory (mlform default: false).
        mappedTo:                  Backend feature name or model input position.
        valuePath:                 Key path used when reading the field value on submit.
        defaultValue:              Initial value for the field.
    """

    model_config = ConfigDict(extra="forbid", frozen=False)

    label: Annotated[str, Field(min_length=1, max_length=100)]
    description: Annotated[str | None, Field(max_length=500)] = None
    required: bool = False
    mappedTo: MappedToTarget
    valuePath: str | list[str] | None = None
    defaultValue: Any | None = None
