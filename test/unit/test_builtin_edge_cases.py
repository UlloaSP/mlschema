# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
from __future__ import annotations

import datetime as dt

import pandas as pd
import pytest
from pandas import Series

from mlschema import FieldContext
from mlschema.strategies import category_builder, number_builder, series_builder


def _ctx(name: str = "field", dtype: str = "object") -> FieldContext:
    return FieldContext(
        name, dtype, True, 0, lambda series: {"kind": "text", "label": str(series.name)}
    )


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        (["A", "A", "B"], ["A", "B"]),
        (["A", None, "B", pd.NA], ["A", "B"]),
        (["", "A", ""], ["", "A"]),
        ([" ", "\t", "\n"], [" ", "\t", "\n"]),
        (["cafe", "naive", "resume"], ["cafe", "naive", "resume"]),
    ],
)
def test_category_builder_extracts_unique_non_null_options(values, expected):
    """Validates option extraction across common object-value edge cases."""
    field = category_builder(Series(values), _ctx(dtype="category"))

    assert field["options"] == expected


@pytest.mark.parametrize(
    "values",
    [
        [9223372036854775807, -9223372036854775808, 0],
        [-5, -10, -1],
        [0, 0, 0],
        [42],
        [5, 5, 5],
    ],
)
def test_number_builder_uses_integer_step_for_integer_edge_values(values):
    """Validates integer edge values keep step 1."""
    field = number_builder(Series(values, dtype="int64"), _ctx(dtype="int64"))

    assert field["step"] == 1


@pytest.mark.parametrize(
    "values",
    [
        [1.7976931348623157e308, -1.7976931348623157e308],
        [1e10, 1e-10, 2.5e5],
        [-100.5, 0.0, 100.5],
        [3.14],
        [2.5, 2.5, 2.5],
        [float("inf"), float("-inf"), 1.0],
    ],
)
def test_number_builder_uses_float_step_for_float_edge_values(values):
    """Validates float edge values keep step 0.1."""
    field = number_builder(Series(values, dtype="float64"), _ctx(dtype="float64"))

    assert field["step"] == 0.1


@pytest.mark.parametrize(
    ("values", "first_label", "second_label"),
    [
        ([(1, 2), (3, 4)], "field1", "field2"),
        ([[1, 2], [3, 4]], "field1", "field2"),
        ([{"x": 1, "y": 2}, {"x": 3, "y": 4}], "x", "y"),
    ],
)
def test_series_builder_extracts_supported_pair_shapes(
    values, first_label, second_label
):
    """Validates tuple/list/dict series cells split into two sub-fields."""
    field = series_builder(Series(values), _ctx("pair"))

    assert field["field1"]["label"] == first_label
    assert field["field2"]["label"] == second_label


@pytest.mark.parametrize(
    "values",
    [
        [],
        [None, None],
        [(1, 2, 3)],
        [[1]],
        [{"x": 1}],
        ["not-a-pair"],
    ],
)
def test_series_builder_rejects_non_pair_shapes(values):
    """Validates series builder rejects empty, null-only, and malformed cells."""
    assert series_builder(Series(values, dtype="object"), _ctx("bad")) is None


@pytest.mark.parametrize(
    "values",
    [
        [(dt.date(2024, 1, 1), 1.5)],
        [(dt.datetime(2024, 1, 1), 1.5)],
        [("2024-01-01", "2.5")],
    ],
)
def test_series_builder_coerces_subseries_before_recursive_inference(values):
    """Validates sub-series coercion runs before recursive inference callback."""
    seen_dtypes: list[str] = []

    def infer_field(series: Series) -> dict:
        seen_dtypes.append(str(series.dtype))
        return {"kind": "text", "label": str(series.name)}

    ctx = FieldContext("series", "object", True, 0, infer_field)
    series_builder(Series(values), ctx)

    assert seen_dtypes
    assert any(dtype != "object" for dtype in seen_dtypes)
