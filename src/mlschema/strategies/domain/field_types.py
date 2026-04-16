# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
from enum import Enum


class FieldTypes(str, Enum):
    TEXT = "text"
    NUMBER = "number"
    BOOLEAN = "boolean"
    CATEGORY = "category"
    DATE = "date"
