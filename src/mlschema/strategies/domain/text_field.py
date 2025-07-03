"""mlschema.strategies.domain.text_field
======================================
Modelo Pydantic para campos **texto**.

Amplía :class:`mlschema.core.domain.BaseField` fijando ``type='text'`` y
proporcionando validación opcional de longitud y patrón.

Atributos adicionales
--------------------
* ``value``       - Valor actual (opcional).
* ``placeholder`` - Texto guía para el front-end.
* ``minLength``   - Longitud mínima permitida.
* ``maxLength``   - Longitud máxima permitida.
* ``pattern``     - Expresión regular Python (como *string*).

El validador ``_check_lengths`` comprueba coherencia entre ``minLength``
y ``maxLength``.

Ejemplo de uso
--------------
>>> from mlschema.strategies.domain.text_field import TextField
>>> TextField(title="comentario", minLength=1, maxLength=50, value="ok").model_dump()["value"]
'ok'
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from mlschema.core.domain import BaseField
from mlschema.strategies.domain.field_types import FieldTypes

__all__ = ["TextField"]


class TextField(BaseField):
    """Schema Pydantic para un campo de texto."""

    type: Literal[FieldTypes.TEXT] = FieldTypes.TEXT
    value: str | None = None
    placeholder: str | None = None
    minLength: int | None = None
    maxLength: int | None = None
    pattern: str | None = Field(
        default=None,
        description=(
            "Expresión regular en notación Python; Pydantic no conserva "
            "instancias de re.Pattern en JSON-serialización."
        ),
    )

    @model_validator(mode="after")
    def _check_lengths(self) -> TextField:
        """Valida que *minLength* ≤ *maxLength*.

        Returns
        -------
        TextField
            Instancia validada.

        Raises
        ------
        ValueError
            Si las longitudes son incoherentes.
        """
        if (
            self.minLength is not None
            and self.maxLength is not None
            and self.minLength > self.maxLength
        ):
            raise ValueError(
                f"minLength ({self.minLength}) debe ser ≤ maxLength ({self.maxLength})"
            )
        return self
