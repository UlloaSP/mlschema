# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
from __future__ import annotations

import pandas as pd
from pandas import Series

from mlschema import FieldContext
from mlschema.strategies import (
    boolean_builder,
    category_builder,
    date_builder,
    number_builder,
    series_builder,
    text_builder,
)


def _ctx(name: str, dtype: str, required: bool = True) -> FieldContext:
    return FieldContext(name, dtype, required, 0, 0, lambda series: {"kind": "text"})


def test_boolean_builder_claims_only_boolean_dtypes():
    """Validates boolean builder success and non-match paths."""
    assert boolean_builder(Series([True]), _ctx("flag", "bool")) == {
        "kind": "boolean",
        "label": "flag",
        "required": True,
        "mappedTo": 0,
        "description": None,
    }
    assert boolean_builder(Series([1]), _ctx("count", "int64")) is None


def test_category_builder_extracts_ordered_options():
    """Validates categorical options preserve declared pandas category order."""
    dtype = pd.CategoricalDtype(["high", "medium", "low"], ordered=True)
    series = Series(["medium", "high"], dtype=dtype, name="priority")

    assert category_builder(series, _ctx("priority", "category")) == {
        "kind": "category",
        "label": "priority",
        "required": True,
        "mappedTo": 0,
        "description": None,
        "options": ["high", "medium", "low"],
    }
    assert category_builder(Series(["x"]), _ctx("name", "object")) is None


def test_date_builder_claims_supported_datetime_dtypes():
    """Validates date builder supports pandas datetime precision names."""
    assert date_builder(
        Series(pd.date_range("2024-01-01", periods=1)), _ctx("d", "datetime64[us]")
    ) == {
        "kind": "date",
        "label": "d",
        "required": True,
        "mappedTo": 0,
        "description": None,
    }
    assert date_builder(Series([1]), _ctx("n", "int64")) is None


def test_number_builder_preserves_step_rules():
    """Validates int columns use step 1 and float columns use step 0.1."""
    int_field = number_builder(Series([1, 2], dtype="int64"), _ctx("count", "int64"))
    float_field = number_builder(
        Series([1.0, 2.0], dtype="float64"), _ctx("ratio", "float64")
    )

    assert int_field["step"] == 1
    assert float_field["step"] == 0.1
    assert number_builder(Series(["x"]), _ctx("name", "object")) is None


def test_series_builder_infers_tuple_subfields_through_context_callback():
    """Validates series builder splits compound cells and delegates sub-fields."""
    calls: list[str] = []

    def infer_field(series: Series) -> dict:
        calls.append(str(series.name))
        return {
            "kind": "text",
            "label": str(series.name),
            "required": True,
            "mappedTo": 0,
        }

    ctx = FieldContext("readings", "object", True, 0, 0, infer_field)
    field = series_builder(Series([(1, "a"), (2, "b")]), ctx)

    assert field["kind"] == "series"
    assert field["field1"]["label"] == "field1"
    assert field["field2"]["label"] == "field2"
    assert calls == ["field1", "field2"]
    assert series_builder(Series(["x"]), ctx) is None


def test_text_builder_is_total_fallback():
    """Validates text builder always emits a valid text field."""
    assert text_builder(Series([object()]), _ctx("anything", "complex128")) == {
        "kind": "text",
        "label": "anything",
        "required": True,
        "mappedTo": 0,
        "description": None,
    }
