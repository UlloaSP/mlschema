# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
from __future__ import annotations

from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field


class BaseReport(BaseModel):
    """Standard metadata present in **all** reports.

    Aligns with mlform's ``BaseReportConfig``.  Extend this class to define
    custom report types.

    Attributes:
        label:       Human-readable report title (max 100 chars).
        description: Optional help text (max 500 chars).
        source:      Key used to locate the report payload in the submit result.
        ui:          Arbitrary UI-layer props forwarded to the component.
    """

    model_config = ConfigDict(extra="forbid", frozen=False)

    label: Annotated[str | None, Field(max_length=100)] = None
    description: Annotated[str | None, Field(max_length=500)] = None
    source: str | None = None
    ui: dict[str, Any] | None = None
