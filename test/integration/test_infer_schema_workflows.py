# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
from __future__ import annotations

from typing import Literal

import pandas as pd
from pandas import DataFrame, Series

from mlschema import BaseField, FieldContext, infer_schema, kind


def test_infer_schema_end_to_end_with_builtins_and_overrides():
    """Validates common production workflow using all builtin field kinds."""
    df = DataFrame(
        {
            "id": [1, 2, 3],
            "price": [1.5, 2.5, 3.5],
            "name": ["Ada", "Linus", "Grace"],
            "active": [True, False, True],
            "created": pd.date_range("2024-01-01", periods=3),
            "tier": pd.Categorical(["pro", "free", "pro"]),
            "reading": [(pd.Timestamp("2024-01-01"), 23.5)] * 3,
        }
    )

    fields = infer_schema(df, overrides={"price": {"unit": "EUR", "min": 0}})

    assert [field["kind"] for field in fields] == [
        "number",
        "number",
        "text",
        "boolean",
        "date",
        "category",
        "series",
    ]
    assert fields[1]["unit"] == "EUR"
    assert fields[5]["options"] == ["free", "pro"]
    assert fields[6]["field1"]["kind"] == "date"
    assert fields[6]["field2"]["kind"] == "number"


def test_infer_schema_end_to_end_with_custom_builder_and_kind():
    """Validates custom builder and new strict kind compose in one run."""

    class DurationField(BaseField):
        kind: Literal["duration"] = "duration"
        unit: Literal["seconds"] = "seconds"
        minSeconds: int
        maxSeconds: int

    def euros(series: Series, ctx: FieldContext) -> dict | None:
        if ctx.name != "amount_eur":
            return None
        return {
            "kind": "number",
            "label": "Amount",
            "required": ctx.required,
            "mappedTo": ctx.mappedTo,
            "step": 0.01,
            "unit": "EUR",
        }

    def duration(series: Series, ctx: FieldContext) -> dict | None:
        if ctx.dtype not in {"timedelta64[ns]", "timedelta64[us]"}:
            return None
        return {
            "kind": "duration",
            "label": ctx.name,
            "required": ctx.required,
            "mappedTo": ctx.mappedTo,
            "minSeconds": int(series.min().total_seconds()),
            "maxSeconds": int(series.max().total_seconds()),
        }

    fields = infer_schema(
        DataFrame(
            {
                "amount_eur": [1.2, 3.4],
                "duration": pd.timedelta_range("1 day", periods=2, freq="D"),
            }
        ),
        builders=[euros],
        kinds=[kind(model=DurationField, infer=duration)],
    )

    assert fields[0]["unit"] == "EUR"
    assert fields[0]["step"] == 0.01
    assert fields[1]["kind"] == "duration"
    assert fields[1]["unit"] == "seconds"


def test_infer_schema_maps_named_columns_and_onehot_groups():
    """Validates named DataFrame columns drive labels and mappedTo strings."""
    df = DataFrame(
        {
            "color__red": [1, 0],
            "color__blue": [0, 1],
            "size": [10, 20],
        }
    )

    fields = infer_schema(df)

    assert fields == [
        {
            "kind": "onehot-category",
            "label": "color",
            "required": True,
            "options": [
                {"label": "red", "value": "red", "mappedTo": "color__red"},
                {"label": "blue", "value": "blue", "mappedTo": "color__blue"},
            ],
        },
        {
            "kind": "number",
            "label": "size",
            "required": True,
            "mappedTo": "size",
            "step": 1,
        },
    ]


def test_infer_schema_uses_named_column_targets():
    """Validates named columns become string mappedTo targets."""
    fields = infer_schema(DataFrame({"age": [1, 2], "name": ["a", "b"]}))

    assert [field["label"] for field in fields] == ["age", "name"]
    assert [field["mappedTo"] for field in fields] == ["age", "name"]


def test_infer_schema_generates_labels_for_positional_columns():
    """Validates unnamed positional columns get feature labels and int targets."""
    fields = infer_schema(DataFrame([[1, "a"], [2, "b"]]))

    assert [field["label"] for field in fields] == ["feature_0", "feature_1"]
    assert [field["mappedTo"] for field in fields] == [0, 1]


def test_infer_schema_keeps_positional_binary_columns_as_fields():
    """Validates positional binary inputs map like fields, not onehot groups."""
    fields = infer_schema(DataFrame([[1, 0, 10], [0, 1, 20]]))

    assert [field["kind"] for field in fields] == ["number", "number", "number"]
    assert [field["label"] for field in fields] == [
        "feature_0",
        "feature_1",
        "feature_2",
    ]
    assert [field["mappedTo"] for field in fields] == [0, 1, 2]
