"""mlschema.strategies.domain.date_field
=======================================
Modelo Pydantic para campos **fecha/hora**.

Extiende :class:`mlschema.core.domain.BaseField` fijando el atributo
``type`` a ``"date"`` y añadiendo metadatos específicos:

* ``value`` - Fecha seleccionada (opcional).
* ``min``   - Fecha mínima permitida.
* ``max``   - Fecha máxima permitida.
* ``step``  - Incremento en días (``PositiveInt``).

El validador ``_check_dates`` impone coherencia interna entre ``min``,
``max`` y ``value``.

Ejemplo de uso
--------------
>>> from datetime import date
>>> from mlschema.strategies.domain.date_field import DateField
>>> DateField(title="inicio", min=date(2024, 1, 1), max=date(2024, 12, 31)).model_dump()
{'title': 'inicio', 'description': None, 'required': True, 'type': 'date', 'value': None, 'min': datetime.date(2024, 1, 1), 'max': datetime.date(2024, 12, 31), 'step': 1}
"""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import PositiveInt, model_validator

from mlschema.core.domain import BaseField
from mlschema.strategies.domain.field_types import FieldTypes


class DateField(BaseField):
    """Schema Pydantic para un campo de fecha/hora."""

    type: Literal[FieldTypes.DATE] = FieldTypes.DATE
    value: date | None = None
    min: date | None = None
    max: date | None = None
    step: PositiveInt = 1

    @model_validator(mode="after")
    def _check_dates(self) -> "DateField":
        """Valida la coherencia entre *min*, *max* y *value*.

        Returns
        -------
        DateField
            Instancia validada.

        Raises
        ------
        ValueError
            Si las fechas son incoherentes.
        """
        if self.min and self.max and self.min > self.max:
            raise ValueError(
                "La fecha mínima debe ser anterior o igual a la fecha máxima"
            )

        if self.value:
            if self.min and self.value < self.min:
                raise ValueError(
                    "La fecha debe ser posterior o igual a la fecha mínima"
                )
            if self.max and self.value > self.max:
                raise ValueError("La fecha debe ser anterior o igual a la fecha máxima")
        return self
