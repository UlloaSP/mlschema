"""mlschema.strategies.domain.field_types
========================================
Enumeración de **tipos de campo** admitidos por *mlschema*.

La clase :class:`FieldTypes` centraliza los literales que se utilizan en
las *FieldStrategy* y los modelos Pydantic de dominio, garantizando
consistencia en todo el proyecto.

Valores disponibles
-------------------
* ``TEXT``      – Cadena ``"text"``.
* ``NUMBER``    – Cadena ``"number"``.
* ``BOOLEAN``   – Cadena ``"boolean"``.
* ``CATEGORY``  – Cadena ``"category"``.
* ``DATE``      – Cadena ``"date"``.

Ejemplo de uso
--------------
>>> from mlschema.strategies.domain.field_types import FieldTypes
>>> FieldTypes.TEXT.value
'text'
"""

from __future__ import annotations

from enum import Enum

__all__ = ["FieldTypes"]


class FieldTypes(str, Enum):
    """Tipos de campo reconocidos por el *schema*."""

    TEXT = "text"
    NUMBER = "number"
    BOOLEAN = "boolean"
    CATEGORY = "category"
    DATE = "date"
