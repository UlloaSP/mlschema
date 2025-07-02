"""mlschema.core.domain.base_field
==================================
Modelo Pydantic base que encapsula los metadatos **comunes** de cualquier
campo generado por *mlschema*.

- ``title``       – Nombre legible del campo (habitualmente el nombre de la
  columna en el *DataFrame*).
- ``description`` – Texto opcional que amplía el significado del campo.
- ``required``    – Indica si la columna carece de valores nulos.

Ejemplo mínimo
--------------
>>> from mlschema.core.domain import BaseField
>>> BaseField(title="age", required=False).model_dump()
{'title': 'age', 'description': None, 'required': False}

El modelo utiliza ``extra='forbid'`` para evitar claves no declaradas y
se mantiene mutable (``frozen=False``) a fin de que las *FieldStrategy*
puedan ajustar los valores antes de la serialización final.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class BaseField(BaseModel):
    """Metadatos estándar presentes en **todos** los campos.

    Attributes
    ----------
    title:
        Identificador legible del campo (1‑100 caracteres).
    description:
        Descripción opcional (máx. 500 caracteres).
    required:
        ``True`` si la columna original no contiene valores nulos.
    """

    model_config = ConfigDict(extra="forbid", frozen=False)

    title: Annotated[str, Field(min_length=1, max_length=100)]
    description: Annotated[str | None, Field(max_length=500)] = None
    required: bool = True
