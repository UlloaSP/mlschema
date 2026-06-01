# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
from __future__ import annotations

import pandas as pd
from pandas import DataFrame

from mlschema import infer_schema


def test_infer_schema_handles_many_rows_and_columns_without_contract_drift():
    """Validates inference remains correct under a wide, moderately large load."""
    rows = 2_000
    data = {
        **{f"num_{i}": range(rows) for i in range(20)},
        **{f"txt_{i}": [f"value-{j}" for j in range(rows)] for i in range(20)},
        **{f"flag_{i}": [j % 2 == 0 for j in range(rows)] for i in range(10)},
    }

    fields = infer_schema(DataFrame(data))

    assert len(fields) == 50
    assert [field["kind"] for field in fields[:20]] == ["number"] * 20
    assert [field["kind"] for field in fields[20:40]] == ["text"] * 20
    assert [field["kind"] for field in fields[40:]] == ["boolean"] * 10
    assert all(field["required"] is True for field in fields)


def test_infer_schema_handles_large_categorical_option_sets():
    """Validates category option extraction remains complete under larger inputs."""
    categories = [f"cat_{i}" for i in range(500)]
    df = DataFrame({"segment": pd.Categorical(categories * 2, categories=categories)})

    fields = infer_schema(df)

    assert fields == [
        {
            "kind": "category",
            "label": "segment",
            "required": True,
            "options": categories,
        }
    ]
