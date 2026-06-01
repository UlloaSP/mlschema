# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
from enum import Enum


class ReportTypes(str, Enum):
    REGRESSOR = "regressor"
    CLASSIFIER = "classifier"
