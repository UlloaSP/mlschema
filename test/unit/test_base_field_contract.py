# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
from __future__ import annotations

import pytest
from pydantic import ValidationError

from mlschema import BaseField


class MinimalField(BaseField):
    kind: str = "minimal"


@pytest.mark.parametrize(
    "kwargs",
    [
        {"description": "Short help"},
        {"disabled": True},
        {"hidden": False},
        {"readOnly": True},
        {"disabledWhen": {"field": "x"}},
        {"hiddenWhen": {"field": "x"}},
        {"readOnlyWhen": {"field": "x"}},
        {"asyncValidationDebounceMs": 250},
        {"inactiveFieldPolicy": "include"},
        {"inactiveFieldPolicy": "omit"},
        {"inactiveFieldPolicy": "reset-on-hide"},
        {"valuePath": "payload.name"},
        {"valuePath": ["payload", "name"]},
        {"defaultValue": "Ada"},
        {"ui": {"placeholder": "Name"}},
    ],
)
def test_base_field_accepts_optional_contract_attributes(kwargs):
    """Validates BaseField optional attributes remain accepted."""
    assert MinimalField(label="name", **kwargs).kind == "minimal"


@pytest.mark.parametrize(
    "kwargs",
    [
        {"label": ""},
        {"label": "x" * 101},
        {"label": "ok", "description": "x" * 501},
        {"label": "ok", "inactiveFieldPolicy": "drop"},
        {"label": "ok", "extra": "forbidden"},
    ],
)
def test_base_field_rejects_invalid_contract_attributes(kwargs):
    """Validates BaseField rejects invalid reserved contract attributes."""
    with pytest.raises(ValidationError):
        MinimalField(**kwargs)
