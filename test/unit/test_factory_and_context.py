# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
from __future__ import annotations

import pytest

from mlschema import FieldContext
from mlschema.strategies.app import builtin_kinds


def test_builtin_kinds_return_expected_order():
    """Validates builtin inference order stays most-specific to fallback."""
    assert [item.name for item in builtin_kinds()] == [
        "series",
        "onehot-category",
        "boolean",
        "category",
        "date",
        "number",
        "text",
    ]


@pytest.mark.parametrize(
    "kind_name",
    ["series", "onehot-category", "boolean", "category", "date", "number", "text"],
)
def test_builtin_kinds_have_callable_inference(kind_name: str):
    """Validates each builtin kind exposes a callable inference function."""
    item = next(kind for kind in builtin_kinds() if kind.name == kind_name)

    assert callable(item.infer)


@pytest.mark.parametrize(
    ("name", "dtype", "required", "index"),
    [
        ("age", "int64", True, 0),
        ("name", "object", False, 1),
        ("created", "datetime64[us]", True, 2),
        ("tier", "category", False, 3),
    ],
)
def test_field_context_preserves_column_metadata(name, dtype, required, index):
    """Validates FieldContext stores metadata passed to builders."""
    ctx = FieldContext(
        name, dtype, required, index, index, lambda series: {"kind": "text"}
    )

    assert ctx.name == name
    assert ctx.dtype == dtype
    assert ctx.required is required
    assert ctx.index == index
    assert ctx.mappedTo == index
