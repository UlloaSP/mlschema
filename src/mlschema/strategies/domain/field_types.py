"""mlschema.strategies.domain.field_types
========================================
Enumeration of **field types** supported by *mlschema*.

The :class:`FieldTypes` class centralizes the literals used in
*FieldStrategy* and Pydantic domain models, ensuring
consistency throughout the project.

Available values
----------------
* ``TEXT``      - String ``"text"``.
* ``NUMBER``    - String ``"number"``.
* ``BOOLEAN``   - String ``"boolean"``.
* ``CATEGORY``  - String ``"category"``.
* ``DATE``      - String ``"date"``.

"""

from __future__ import annotations

from enum import Enum


class FieldTypes(str, Enum):
    """Field types recognized by the *schema*."""

    TEXT = "text"
    NUMBER = "number"
    BOOLEAN = "boolean"
    CATEGORY = "category"
    DATE = "date"
