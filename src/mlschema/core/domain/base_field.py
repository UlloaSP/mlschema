# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class BaseField(BaseModel):
    """Standard metadata present in **all** fields.

    Aligns with mlform's ``BaseFieldConfig``.  Extend this class to define
    custom field types.

    Attributes:
        label:                     Human-readable field identifier (1-100 chars).
        description:               Optional help text (max 500 chars).
        required:                  Field is mandatory (mlform default: false).
        disabled:                  Field is disabled (mlform default: false).
        hidden:                    Field is hidden (mlform default: false).
        readOnly:                  Field is read-only (mlform default: false).
        disabledWhen:              Declarative condition to disable the field.
        hiddenWhen:                Declarative condition to hide the field.
        readOnlyWhen:              Declarative condition to make field read-only.
        asyncValidationDebounceMs: Debounce in ms for async validation.
        inactiveFieldPolicy:       Behaviour when field becomes inactive.
        valuePath:                 Key path used when reading the field value on submit.
        defaultValue:              Initial value for the field.
        ui:                        Arbitrary UI-layer props forwarded to the component.
    """

    model_config = ConfigDict(extra="forbid", frozen=False)

    label: Annotated[str, Field(min_length=1, max_length=100)]
    description: Annotated[str | None, Field(max_length=500)] = None
    required: bool = False
    disabled: bool | None = None
    hidden: bool | None = None
    readOnly: bool | None = None
    disabledWhen: Any | None = None
    hiddenWhen: Any | None = None
    readOnlyWhen: Any | None = None
    asyncValidationDebounceMs: int | None = None
    inactiveFieldPolicy: Literal["include", "omit", "reset-on-hide"] | None = None
    valuePath: str | list[str] | None = None
    defaultValue: Any | None = None
    ui: dict[str, Any] | None = None
