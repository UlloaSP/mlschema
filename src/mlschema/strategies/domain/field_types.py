# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
from enum import StrEnum


class FieldTypes(StrEnum):
    TEXT = "text"
    NUMBER = "number"
    BOOLEAN = "boolean"
    CATEGORY = "category"
    ONEHOT_CATEGORY = "onehot-category"
    DATE = "date"
    SERIES = "series"
