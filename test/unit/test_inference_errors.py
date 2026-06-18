# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
from __future__ import annotations

from typing import Literal

import pytest
from pandas import DataFrame, Series
from pydantic import ValidationError

from mlschema import BaseField, FieldContext, infer_schema, kind
from mlschema.core.exceptions import (
    EmptyDataFrameError,
    FieldBuilderError,
    FieldKindAlreadyRegisteredError,
    MLSchemaError,
    UnknownFieldKindError,
)
from mlschema.strategies.domain import NumberField


def test_infer_schema_rejects_empty_dataframes():
    """Validates empty row and empty column inputs raise EmptyDataFrameError."""
    with pytest.raises(EmptyDataFrameError):
        infer_schema(DataFrame(columns=["name"]))
    with pytest.raises(EmptyDataFrameError):
        infer_schema(DataFrame())


def test_infer_schema_rejects_overrides_for_missing_columns():
    """Validates overrides cannot silently target absent DataFrame columns."""
    with pytest.raises(FieldBuilderError):
        infer_schema(DataFrame({"age": [25]}), overrides={"missing": {"min": 0}})


def test_infer_schema_rejects_builder_returning_non_dict():
    """Validates builders must return a dict or None."""

    def bad_return(_series: Series, _ctx: FieldContext) -> str:
        return "bad"

    with pytest.raises(FieldBuilderError):
        infer_schema(DataFrame({"x": [1]}), builders=[bad_return])  # type: ignore[list-item]


def test_infer_schema_rejects_builder_output_without_kind():
    """Validates builder outputs must include a kind discriminator."""

    def missing_kind(_series: Series, ctx: FieldContext) -> dict:
        return {"label": ctx.name, "required": ctx.required}

    with pytest.raises(FieldBuilderError):
        infer_schema(DataFrame({"x": [1]}), builders=[missing_kind])


def test_infer_schema_rejects_unknown_generated_kind():
    """Validates unregistered custom kinds are rejected before output escapes."""

    def unknown(_series: Series, ctx: FieldContext) -> dict:
        return {
            "kind": "missing",
            "label": ctx.name,
            "required": ctx.required,
            "mappedTo": ctx.mappedTo,
        }

    with pytest.raises(UnknownFieldKindError):
        infer_schema(DataFrame({"x": [1]}), builders=[unknown])


def test_infer_schema_rejects_duplicate_kind_models():
    """Validates custom kinds cannot collide with builtin kind names."""

    def builder(_series: Series, ctx: FieldContext) -> dict:
        return {
            "kind": "number",
            "label": ctx.name,
            "required": ctx.required,
            "mappedTo": ctx.mappedTo,
        }

    with pytest.raises(FieldKindAlreadyRegisteredError):
        infer_schema(
            DataFrame({"x": [1]}), kinds=[kind(model=NumberField, infer=builder)]
        )


def test_infer_schema_surfaces_pydantic_validation_errors():
    """Validates final fields are checked by their strict Pydantic model."""
    with pytest.raises(ValidationError):
        infer_schema(DataFrame({"age": [25]}), overrides={"age": {"min": 10, "max": 1}})


def test_custom_kind_invalid_payload_raises_validation_error():
    """Validates custom kind models enforce required custom attributes."""

    class GeoField(BaseField):
        kind: Literal["geo"] = "geo"
        latKey: str

    def geo(_series: Series, ctx: FieldContext) -> dict:
        return {
            "kind": "geo",
            "label": ctx.name,
            "required": ctx.required,
            "mappedTo": ctx.mappedTo,
        }

    with pytest.raises(ValidationError):
        infer_schema(
            DataFrame({"location": ["x"]}), kinds=[kind(model=GeoField, infer=geo)]
        )


@pytest.mark.parametrize(
    "raising_call",
    [
        lambda: infer_schema(DataFrame()),
        lambda: infer_schema(
            DataFrame({"age": [1]}), overrides={"missing": {"min": 0}}
        ),
        lambda: infer_schema(DataFrame({"x": [1]}), builders=[lambda _s, _c: "bad"]),  # type: ignore[list-item]
        lambda: infer_schema(
            DataFrame({"x": [1]}), builders=[lambda _s, c: {"label": c.name}]
        ),
        lambda: infer_schema(
            DataFrame({"x": [1]}),
            builders=[
                lambda _s, c: {"kind": "ghost", "label": c.name, "mappedTo": c.mappedTo}
            ],
        ),
    ],
)
def test_known_mlschema_errors_inherit_from_project_root(raising_call):
    """Validates known MLSchema exceptions share the MLSchemaError root."""
    with pytest.raises(MLSchemaError):
        raising_call()


def test_infer_schema_rejects_empty_onehot_separator():
    """Validates onehot separator cannot be empty."""
    with pytest.raises(FieldBuilderError):
        infer_schema(DataFrame({"x": [1]}), onehot_separator="")
