# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field

from mlschema.core.domain import BaseField
from mlschema.strategies.domain.field_types import FieldTypes

type MappedToTarget = Annotated[str, Field(min_length=1)] | Annotated[int, Field(ge=0)]


class OneHotCategoryOption(BaseModel):
    label: Annotated[str, Field(min_length=1)]
    value: Annotated[str, Field(min_length=1)]
    mappedTo: MappedToTarget


class OneHotCategoryField(BaseField):
    kind: Literal[FieldTypes.ONEHOT_CATEGORY] = FieldTypes.ONEHOT_CATEGORY
    mappedTo: None = Field(default=None, exclude=True)
    defaultValue: str | None = None
    options: Annotated[list[OneHotCategoryOption], Field(min_length=1)]
