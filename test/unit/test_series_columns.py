"""Series columns: native MLForm output, strict kinds and invalid contracts."""

from copy import deepcopy
from typing import Literal

import pandas as pd
import pytest
from pydantic import ValidationError

from mlschema import BaseField, infer_schema, kind
from mlschema.strategies.domain import SeriesField
from mlschema.strategies.domain.series_column import add_series_sub_field


def columns():
    return [
        {"id": "field1", "kind": "text", "label": "x"},
        {"id": "field2", "kind": "number", "label": "y", "step": 1},
    ]


@pytest.mark.parametrize(
    "points", [{}, {"minPoints": 1}, {"maxPoints": 2}, {"minPoints": 1, "maxPoints": 2}]
)
def test_series_accepts_ordered_columns_and_point_bounds(points):
    value = SeriesField(label="s", mappedTo="s", columns=columns(), **points)
    assert [column["id"] for column in value.columns] == ["field1", "field2"]
    assert all("mappedTo" not in column for column in value.model_dump()["columns"])


@pytest.mark.parametrize(
    "change",
    [
        lambda c: c.reverse(),
        lambda c: c.pop(),
        lambda c: c.append(deepcopy(c[0])),
        lambda c: c.__setitem__(0, "invalid"),
        lambda c: c[0].update(id="field2"),
        lambda c: c[0].update(id="unknown"),
        lambda c: c[0].pop("id"),
        lambda c: c[0].update(mappedTo=0),
        lambda c: c[0].update(kind="series"),
        lambda c: c[0].update(kind="onehot-category"),
        lambda c: c[0].update(kind="unknown"),
        lambda c: c[0].update(extra="private"),
        lambda c: c[1].update(min=5, max=1),
        lambda c: c[0].update(minLength=3, defaultValue="x"),
    ],
)
def test_series_rejects_invalid_columns(change):
    value = columns()
    change(value)
    with pytest.raises(ValidationError):
        SeriesField(label="s", mappedTo=0, columns=value)


@pytest.mark.parametrize(
    "points", [{"minPoints": 0}, {"maxPoints": 0}, {"minPoints": 2, "maxPoints": 1}]
)
def test_series_rejects_invalid_point_bounds(points):
    with pytest.raises(ValidationError):
        SeriesField(label="s", mappedTo=0, columns=columns(), **points)


def test_series_inference_emits_columns_directly():
    field = infer_schema(pd.DataFrame({"pair": [{"x": 1, "y": 2.5}]}))[0]
    assert set(field) == {"kind", "label", "required", "mappedTo", "columns"}
    assert field["columns"] == [
        {"id": "field1", "kind": "number", "label": "x", "required": True, "step": 1},
        {"id": "field2", "kind": "number", "label": "y", "required": True, "step": 0.1},
    ]


def test_series_preserves_custom_kind_validation():
    class TagField(BaseField):
        kind: Literal["series-test-tag"] = "series-test-tag"
        token: int

    def builder(series, ctx):
        if ctx.name == "x":
            return {
                "kind": "series-test-tag",
                "label": ctx.name,
                "mappedTo": ctx.mappedTo,
                "token": 42,
            }
        return None

    fields = infer_schema(
        pd.DataFrame({"pair": [{"x": "hello", "y": 2}]}),
        kinds=[kind(model=TagField, infer=builder)],
    )
    assert fields[0]["columns"][0]["token"] == 42
    invalid = fields[0]
    invalid["columns"][0].pop("token")
    with pytest.raises(ValidationError):
        SeriesField(**invalid)


def test_series_cannot_register_as_column_kind():
    with pytest.raises(ValueError, match="scalar"):
        add_series_sub_field(SeriesField)
