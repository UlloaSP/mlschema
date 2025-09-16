from enum import Enum


class FieldTypes(str, Enum):
    TEXT = "text"
    NUMBER = "number"
    BOOLEAN = "boolean"
    CATEGORY = "category"
    DATE = "date"
