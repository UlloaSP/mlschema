# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
from __future__ import annotations

from typing import Literal

import pytest
from pandas import Series

from mlschema import BaseField, FieldContext, kind
from mlschema.core.exceptions import FieldKindError


def test_kind_extracts_name_from_model_literal_default():
    """Validates custom kind names have one source of truth: the model."""

    class GeoField(BaseField):
        kind: Literal["geo"] = "geo"
        latKey: str

    def geo(_series: Series, ctx: FieldContext) -> dict | None:
        return {
            "kind": "geo",
            "label": ctx.name,
            "required": ctx.required,
            "latKey": "lat",
        }

    field_kind = kind(model=GeoField, infer=geo)

    assert field_kind.name == "geo"
    assert field_kind.model is GeoField
    assert field_kind.infer is geo


def test_kind_rejects_non_basefield_models():
    """Validates strict kind registration rejects non-BaseField models."""

    def builder(_series: Series, ctx: FieldContext) -> dict | None:
        return {"kind": "x", "label": ctx.name, "required": ctx.required}

    with pytest.raises(FieldKindError):
        kind(model=object, infer=builder)  # type: ignore[arg-type]
