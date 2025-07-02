"""mlschema.strategies.domain.number_field
========================================
Modelo Pydantic para campos **numéricos** (enteros o flotantes).

Basado en :class:`mlschema.core.domain.BaseField`, añade los siguientes
atributos:

* ``min`` / ``max`` - Cotas inferior y superior permitidas.
* ``step``          - Incremento por defecto (``1`` si no se especifica).
* ``placeholder``   - Texto guía para el front-end.
* ``value``         - Valor actual (opcional).
* ``unit``          - Unidad de medida (p. ej. "kg", "€").

El validador ``_check_numeric_constraints`` asegura coherencia entre las
cotas y el valor.

Ejemplo de uso
--------------
>>> from mlschema.strategies.domain.number_field import NumberField
>>> NumberField(title="edad", min=0, max=120, value=30).model_dump()["value"]
30
"""

from __future__ import annotations

from typing import Literal

from pydantic import model_validator

from mlschema.core.domain import BaseField
from mlschema.strategies.domain.field_types import FieldTypes


class NumberField(BaseField):
    """Schema Pydantic para un campo numérico."""

    type: Literal[FieldTypes.NUMBER] = FieldTypes.NUMBER
    min: float | None = None
    max: float | None = None
    step: float | None = 1
    placeholder: str | None = None
    value: float | None = None
    unit: str | None = None

    @model_validator(mode="after")
    def _check_numeric_constraints(self) -> "NumberField":
        """Valida que *min* ≤ *value* ≤ *max*.

        Returns
        -------
        NumberField
            Instancia validada.

        Raises
        ------
        ValueError
            Si las cotas no son coherentes.
        """
        if self.min is not None and self.max is not None and self.min > self.max:
            raise ValueError(f"min ({self.min}) debe ser ≤ max ({self.max})")

        if self.value is not None:
            if self.min is not None and self.value < self.min:
                raise ValueError(f"value ({self.value}) debe ser ≥ min ({self.min})")
            if self.max is not None and self.value > self.max:
                raise ValueError(f"value ({self.value}) debe ser ≤ max ({self.max})")
        return self
