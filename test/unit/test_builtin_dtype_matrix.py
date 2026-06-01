# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
from __future__ import annotations

import pandas as pd
import pytest
from pandas import Series

from mlschema import FieldContext
from mlschema.strategies import (
    boolean_builder,
    category_builder,
    date_builder,
    number_builder,
    text_builder,
)


def _ctx(dtype: str) -> FieldContext:
    return FieldContext("field", dtype, True, 0, lambda series: {})


@pytest.mark.parametrize("dtype", ["bool", "boolean"])
def test_boolean_builder_accepts_supported_dtypes(dtype: str):
    """Validates every supported boolean dtype is claimed."""
    assert boolean_builder(Series([True]), _ctx(dtype))["kind"] == "boolean"


@pytest.mark.parametrize(
    "dtype",
    [
        "int64",
        "float64",
        "int32",
        "float32",
        "object",
        "string",
        "category",
        "datetime64[ns]",
    ],
)
def test_boolean_builder_rejects_non_boolean_dtypes(dtype: str):
    """Validates boolean builder declines every non-boolean builtin dtype."""
    assert boolean_builder(Series([1]), _ctx(dtype)) is None


@pytest.mark.parametrize("dtype", ["int64", "int32", "float64", "float32"])
def test_number_builder_accepts_supported_dtypes(dtype: str):
    """Validates every supported numeric dtype is claimed."""
    series = Series([1, 2], dtype=dtype)

    assert number_builder(series, _ctx(dtype))["kind"] == "number"


@pytest.mark.parametrize(
    "dtype",
    [
        "bool",
        "boolean",
        "object",
        "string",
        "str",
        "category",
        "datetime64[ns]",
        "datetime64[us]",
    ],
)
def test_number_builder_rejects_non_numeric_dtypes(dtype: str):
    """Validates number builder declines every non-numeric builtin dtype."""
    assert number_builder(Series([1]), _ctx(dtype)) is None


@pytest.mark.parametrize("dtype", ["datetime64[ns]", "datetime64[us]", "datetime64"])
def test_date_builder_accepts_supported_datetime_dtypes(dtype: str):
    """Validates every supported datetime dtype name is claimed."""
    assert (
        date_builder(Series(pd.date_range("2024-01-01", periods=1)), _ctx(dtype))[
            "kind"
        ]
        == "date"
    )


@pytest.mark.parametrize(
    "dtype",
    ["bool", "boolean", "int64", "float64", "object", "string", "str", "category"],
)
def test_date_builder_rejects_non_datetime_dtypes(dtype: str):
    """Validates date builder declines non-datetime dtype names."""
    assert date_builder(Series([1]), _ctx(dtype)) is None


def test_category_builder_accepts_category_dtype():
    """Validates category builder claims pandas category dtype."""
    series = Series(pd.Categorical(["a", "b"]))

    assert category_builder(series, _ctx("category"))["kind"] == "category"


@pytest.mark.parametrize(
    "dtype",
    [
        "bool",
        "boolean",
        "int64",
        "float64",
        "object",
        "string",
        "str",
        "datetime64[ns]",
    ],
)
def test_category_builder_rejects_non_category_dtypes(dtype: str):
    """Validates category builder declines non-category dtype names."""
    assert category_builder(Series(["a"]), _ctx(dtype)) is None


@pytest.mark.parametrize(
    "dtype",
    [
        "bool",
        "boolean",
        "int64",
        "float64",
        "object",
        "string",
        "str",
        "category",
        "datetime64[ns]",
    ],
)
def test_text_builder_accepts_any_dtype_as_fallback(dtype: str):
    """Validates text builder remains total fallback for every dtype."""
    assert text_builder(Series(["x"]), _ctx(dtype))["kind"] == "text"
