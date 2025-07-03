"""mlschema.strategies.domain.boolean_field
==========================================
Pydantic model for **boolean** fields.

Extends :class:`mlschema.core.domain.BaseField` by fixing the
``type`` attribute to the value ``"boolean"`` and adding the ``value`` key that can
be ``True``, ``False`` or ``None``.
"""

from __future__ import annotations

from typing import Literal

from mlschema.core.domain import BaseField
from mlschema.strategies.domain.field_types import FieldTypes


class BooleanField(BaseField):
    """Pydantic schema for a boolean field."""

    type: Literal[FieldTypes.BOOLEAN] = FieldTypes.BOOLEAN
    value: bool | None = None
