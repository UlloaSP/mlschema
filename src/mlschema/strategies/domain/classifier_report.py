# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
from __future__ import annotations

from typing import Literal

from mlschema.core.domain import BaseReport
from mlschema.strategies.domain.report_types import ReportTypes


class ClassifierReport(BaseReport):
    """Report schema for classification model outputs.

    Aligns with mlform's built-in ``classifier`` report kind.

    Attributes:
        kind:         Fixed type identifier ``"classifier"``.
        labels:       Ordered list of class labels (e.g. ``["cat", "dog"]``).
        details:      Whether to show per-class breakdown (mlform default: true).
        explanations: Whether to show feature-importance explanations.
    """

    kind: Literal[ReportTypes.CLASSIFIER] = ReportTypes.CLASSIFIER
    labels: list[str] | None = None
    details: bool | None = None
    explanations: bool | None = None
