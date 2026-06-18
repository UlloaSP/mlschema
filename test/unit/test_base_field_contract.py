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
        {"mappedTo": "name"},
        {"mappedTo": 0},
        {"valuePath": "payload.name"},
        {"valuePath": ["payload", "name"]},
        {"defaultValue": "Ada"},
    ],
)
def test_base_field_accepts_optional_contract_attributes(kwargs):
    """Validates BaseField optional attributes remain accepted."""
    params = {"label": "name", **kwargs}
    params.setdefault("mappedTo", 0)
    assert MinimalField(**params).kind == "minimal"


@pytest.mark.parametrize(
    "kwargs",
    [
        {"label": ""},
        {"label": "x" * 101},
        {"label": "ok", "description": "x" * 501},
        {"label": "ok"},
        {"label": "ok", "mappedTo": None},
        {"label": "ok", "mappedTo": ""},
        {"label": "ok", "mappedTo": -1},
        {"label": "ok", "mappedTo": {"default": "name"}},
        {"label": "ok", "extra": "forbidden"},
    ],
)
def test_base_field_rejects_invalid_contract_attributes(kwargs):
    """Validates BaseField rejects invalid reserved contract attributes."""
    with pytest.raises(ValidationError):
        MinimalField(**kwargs)
