from __future__ import annotations

from typing import Literal

from mlschema.core.domain import BaseField
from mlschema.strategies.domain.field_types import FieldTypes


class BooleanField(BaseField):
    type: Literal[FieldTypes.BOOLEAN] = FieldTypes.BOOLEAN
    value: bool | None = None
