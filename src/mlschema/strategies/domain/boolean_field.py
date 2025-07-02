"""mlschema.strategies.domain.boolean_field
==========================================
Modelo Pydantic para campos **booleanos**.

Extiende :class:`mlschema.core.domain.BaseField` fijando el atributo
``type`` al valor ``"boolean"`` y añadiendo la clave ``value`` que puede
ser ``True``, ``False`` o ``None``.

Ejemplo mínimo
--------------
>>> from mlschema.strategies.domain.boolean_field import BooleanField
>>> BooleanField(title="activo", value=True).model_dump()
{'title': 'activo', 'description': None, 'required': True, 'type': 'boolean', 'value': True}
"""

from __future__ import annotations

from typing import Literal

from mlschema.core.domain import BaseField
from mlschema.strategies.domain.field_types import FieldTypes


class BooleanField(BaseField):
    """Schema Pydantic para un campo booleano."""

    type: Literal[FieldTypes.BOOLEAN] = FieldTypes.BOOLEAN
    value: bool | None = None
