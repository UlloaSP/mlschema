# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
from __future__ import annotations

import pandas as pd
import pytest

from mlschema.core.util import normalize_dtype


@pytest.mark.parametrize(
    ("series", "expected"),
    [
        (pd.Series([1], dtype="int64"), "int64"),
        (pd.Series([1], dtype="int32"), "int32"),
        (pd.Series([1.0], dtype="float64"), "float64"),
        (pd.Series([1.0], dtype="float32"), "float32"),
        (pd.Series([True], dtype="bool"), "bool"),
        (pd.Series(["a"], dtype="object"), "object"),
        (pd.Series(pd.date_range("2024-01-01", periods=1)), "datetime64[us]"),
        (pd.Series([1 + 2j], dtype="complex128"), "complex128"),
    ],
)
def test_normalize_dtype_handles_pandas_series_dtypes(series, expected):
    """Validates pandas and NumPy dtype objects normalize by dtype name."""
    assert normalize_dtype(series.dtype) == expected


@pytest.mark.parametrize(
    ("dtype", "expected"),
    [
        (pd.CategoricalDtype(["A", "B"]), "category"),
        (pd.StringDtype(), "string"),
        ("int64", "int64"),
        ("str", "str"),
        ("datetime64[us]", "datetime64[us]"),
        ("timedelta64[ns]", "timedelta64[ns]"),
        (None, "None"),
        (42, "42"),
        (3.14, "3.14"),
        (True, "True"),
    ],
)
def test_normalize_dtype_handles_extension_strings_and_fallbacks(dtype, expected):
    """Validates extension dtypes, raw strings, and fallback values."""
    assert normalize_dtype(dtype) == expected


def test_normalize_dtype_handles_structured_dtype_by_string():
    """Validates structured dtype-like objects avoid null name leakage."""

    class StructuredDtype:
        name = None
        names = ("x", "y")

        def __str__(self) -> str:
            return "structured"

    assert normalize_dtype(StructuredDtype()) == "structured"


def test_normalize_dtype_handles_name_without_names_attribute():
    """Validates dtype-like objects with only name still normalize correctly."""

    class NamedDtype:
        name = "named"

    assert normalize_dtype(NamedDtype()) == "named"
