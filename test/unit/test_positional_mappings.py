"""Explicit mapping conversion preserves labels/grouping and rejects ambiguity."""

from copy import deepcopy

import pandas as pd
import pytest

from mlschema import infer_schema, with_positional_mappings


def test_converts_named_fields_and_onehot_options_without_mutating_input():
    frame = pd.DataFrame(
        {"age": [5], "color__red": [1], "color__blue": [0], "pair": [(1, 2)]}
    )
    fields = infer_schema(frame)
    original = deepcopy(fields)
    result = with_positional_mappings(fields, list(frame.columns))
    assert result[0]["mappedTo"] == 0
    assert [option["mappedTo"] for option in result[1]["options"]] == [1, 2]
    assert "mappedTo" not in result[1]
    assert result[2]["mappedTo"] == 3
    assert result[2]["columns"] == fields[2]["columns"]
    assert fields == original
    assert with_positional_mappings(result, list(frame.columns)) == result
    result[2]["columns"][0]["label"] = "changed"
    assert fields == original


@pytest.mark.parametrize("names", [["x", "x"], [""], [None], [1], "x"])
def test_rejects_invalid_feature_names(names):
    with pytest.raises(ValueError, match="feature_names"):
        with_positional_mappings([], names)


@pytest.mark.parametrize("target", ["missing", "", -1, 1, True, 0.5, None, [], {}])
def test_rejects_unknown_or_invalid_targets(target):
    with pytest.raises(ValueError, match="target"):
        with_positional_mappings([{"kind": "text", "mappedTo": target}], ["x"])


@pytest.mark.parametrize(
    "options", [None, [], {}, ["x"], [{}], [{"mappedTo": "unknown"}]]
)
def test_rejects_missing_or_invalid_onehot_targets(options):
    with pytest.raises(ValueError):
        with_positional_mappings(
            [{"kind": "onehot-category", "options": options}], ["x"]
        )


def test_empty_schema_and_missing_field_target():
    assert with_positional_mappings([], []) == []
    with pytest.raises(ValueError, match="target"):
        with_positional_mappings([{"kind": "text"}], ["x"])
