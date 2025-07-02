"""mlschema.strategies.domain.category_field
===========================================
Modelo Pydantic para campos **categóricos**.

Amplía :class:`mlschema.core.domain.BaseField` fijando el atributo
``type`` a ``"category"`` y añadiendo:

* ``value``   – Valor actual (opcional).
* ``options`` – Lista de categorías permitidas (mínimo 1 elemento).

El validador ``_check_value_in_options`` garantiza que, si se especifica
``value``, éste aparece dentro de ``options``.

Ejemplo de uso
--------------
>>> from mlschema.strategies.domain.category_field import CategoryField
>>> CategoryField(title="color", options=["A", "B"], value="A").model_dump()
{'title': 'color', 'description': None, 'required': True, 'type': 'category', 'value': 'A', 'options': ['A', 'B']}
"""

from __future__ import annotations

from typing import Annotated, List, Literal

from pydantic import Field, model_validator

from mlschema.core.domain import BaseField
from mlschema.strategies.domain.field_types import FieldTypes


class CategoryField(BaseField):
    """Schema Pydantic para un campo categórico."""

    type: Literal[FieldTypes.CATEGORY] = FieldTypes.CATEGORY
    value: str | None = None
    options: Annotated[List[str], Field(min_length=1)]

    @model_validator(mode="after")
    def _check_value_in_options(self) -> "CategoryField":
        """Valida que ``value`` esté dentro de ``options``.

        Returns
        -------
        CategoryField
            Instancia válida.

        Raises
        ------
        ValueError
            Si ``value`` no pertenece a ``options``.
        """
        if self.value is not None and self.value not in self.options:
            raise ValueError(
                "El valor debe coincidir con una de las opciones permitidas"
            )
        return self
