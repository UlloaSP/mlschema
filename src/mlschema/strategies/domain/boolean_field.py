# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
from __future__ import annotations

from typing import Literal

from mlschema.core.domain import BaseField
from mlschema.strategies.domain.field_types import FieldTypes


class BooleanField(BaseField):
    kind: Literal[FieldTypes.BOOLEAN] = FieldTypes.BOOLEAN
    defaultValue: bool | None = None
    trueLabel: str | None = None
    falseLabel: str | None = None
