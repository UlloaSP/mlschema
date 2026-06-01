# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
from __future__ import annotations

from typing import Literal

from mlschema.core.domain import BaseReport
from mlschema.strategies.domain.report_types import ReportTypes


class RegressorReport(BaseReport):
    """Report schema for regression model outputs.

    Aligns with mlform's built-in ``regressor`` report kind.

    Attributes:
        kind:         Fixed type identifier ``"regressor"``.
        unit:         Unit label for the predicted value (e.g. ``"€"``, ``"kg"``).
        precision:    Decimal places shown (mlform default: 2).
        explanations: Whether to show feature-importance explanations.
    """

    kind: Literal[ReportTypes.REGRESSOR] = ReportTypes.REGRESSOR
    unit: str | None = None
    precision: int | None = None
    explanations: bool | None = None
