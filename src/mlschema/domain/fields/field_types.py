"""
Field types for the schema.
"""

from enum import Enum


class FieldTypes(str, Enum):
    """
    Field types for the schema.
    """

    TEXT = "text"
    NUMBER = "number"
    BOOLEAN = "boolean"
    CATEGORY = "category"
    DATE = "date"
