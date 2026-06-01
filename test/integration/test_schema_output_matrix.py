# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
from __future__ import annotations

import pandas as pd
import pytest
from pandas import DataFrame

from mlschema import infer_schema


@pytest.mark.parametrize(
    ("df", "expected"),
    [
        (
            DataFrame({"x": pd.Series([1, 2], dtype="int64")}),
            {"kind": "number", "step": 1},
        ),
        (
            DataFrame({"x": pd.Series([1, 2], dtype="int32")}),
            {"kind": "number", "step": 1},
        ),
        (
            DataFrame({"x": pd.Series([1.0, 2.0], dtype="float64")}),
            {"kind": "number", "step": 0.1},
        ),
        (
            DataFrame({"x": pd.Series([1.0, 2.0], dtype="float32")}),
            {"kind": "number", "step": 0.1},
        ),
        (DataFrame({"x": pd.Series([True, False], dtype="bool")}), {"kind": "boolean"}),
        (
            DataFrame({"x": pd.Series([True, None], dtype="boolean")}),
            {"kind": "boolean", "required": False},
        ),
        (DataFrame({"x": pd.Series(["a", "b"], dtype="object")}), {"kind": "text"}),
        (DataFrame({"x": pd.Series(["a", "b"], dtype="string")}), {"kind": "text"}),
        (
            DataFrame({"x": pd.Categorical(["b", "a"], categories=["a", "b"])}),
            {"kind": "category", "options": ["a", "b"]},
        ),
        (DataFrame({"x": pd.date_range("2024-01-01", periods=2)}), {"kind": "date"}),
        (DataFrame({"x": [1 + 2j, 3 + 4j]}), {"kind": "text"}),
    ],
)
def test_infer_schema_output_matrix_for_builtin_dtypes(df, expected):
    """Validates end-to-end output for each supported builtin dtype family."""
    field = infer_schema(df)[0]

    for key, value in expected.items():
        assert field[key] == value


@pytest.mark.parametrize(
    ("values", "expected_labels"),
    [
        ([(1, 2)], ("field1", "field2")),
        ([[1, 2]], ("field1", "field2")),
        ([{"left": 1, "right": 2}], ("left", "right")),
    ],
)
def test_infer_schema_output_matrix_for_series_shapes(values, expected_labels):
    """Validates end-to-end series output for every supported compound shape."""
    field = infer_schema(DataFrame({"series": values}))[0]

    assert field["kind"] == "series"
    assert (field["field1"]["label"], field["field2"]["label"]) == expected_labels
