# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
from __future__ import annotations

import pytest
from pydantic import ValidationError

from mlschema.strategies.domain import (
    BooleanField,
    CategoryField,
    DateField,
    NumberField,
    OneHotCategoryField,
    SeriesField,
    TextField,
)


def test_builtin_models_accept_valid_success_cases():
    """Validates every builtin field model accepts a representative valid field."""
    BooleanField(
        label="flag", mappedTo=0, defaultValue=True, trueLabel="yes", falseLabel="no"
    )
    CategoryField(label="tier", mappedTo=1, options=["free", "pro"], defaultValue="pro")
    DateField(label="start", mappedTo=2, min="2024-01-01", max="2024-12-31", step=1)
    NumberField(label="score", mappedTo=3, min=0, max=100, defaultValue=50, step=1)
    TextField(label="name", mappedTo=4, minLength=1, maxLength=20, defaultValue="Ada")
    OneHotCategoryField(
        label="color",
        options=[
            {"label": "Red", "value": "red", "mappedTo": "color__red"},
            {"label": "Blue", "value": "blue", "mappedTo": "color__blue"},
        ],
    )
    SeriesField(
        label="readings",
        mappedTo=5,
        field1={"kind": "text", "label": "x", "mappedTo": 5},
        field2={"kind": "number", "label": "y", "mappedTo": 5, "step": 1},
        minPoints=1,
        maxPoints=2,
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        {"label": "flag", "defaultValue": True},
        {"label": "flag", "trueLabel": "yes"},
        {"label": "flag", "falseLabel": "no"},
        {"label": "flag", "trueLabel": "enabled", "falseLabel": "disabled"},
    ],
)
def test_boolean_model_accepts_optional_display_attributes(kwargs):
    """Validates boolean optional labels and default value success cases."""
    assert BooleanField(mappedTo=0, **kwargs).kind == "boolean"


@pytest.mark.parametrize(
    "kwargs",
    [
        {"min": 10, "max": 1},
        {"min": 10, "defaultValue": 1},
        {"max": 10, "defaultValue": 11},
    ],
)
def test_number_model_rejects_invalid_constraints(kwargs):
    """Validates number min/max/defaultValue exceptions."""
    with pytest.raises(ValidationError):
        NumberField(label="n", mappedTo=0, **kwargs)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"min": 0},
        {"max": 100},
        {"step": 0.1},
        {"placeholder": "0"},
        {"unit": "EUR"},
        {"defaultValue": 10, "min": 0, "max": 100},
    ],
)
def test_number_model_accepts_optional_attributes(kwargs):
    """Validates number optional attributes and valid constraints."""
    assert NumberField(label="n", mappedTo=0, **kwargs).kind == "number"


@pytest.mark.parametrize(
    "kwargs",
    [
        {"minLength": 10, "maxLength": 1},
        {"minLength": 3, "defaultValue": "x"},
        {"maxLength": 1, "defaultValue": "xx"},
    ],
)
def test_text_model_rejects_invalid_constraints(kwargs):
    """Validates text length/defaultValue exceptions."""
    with pytest.raises(ValidationError):
        TextField(label="t", mappedTo=0, **kwargs)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"placeholder": "name"},
        {"minLength": 0},
        {"maxLength": 100},
        {"pattern": "^[a-z]+$"},
        {"defaultValue": "Ada", "minLength": 1, "maxLength": 10},
    ],
)
def test_text_model_accepts_optional_attributes(kwargs):
    """Validates text optional attributes and valid length constraints."""
    assert TextField(label="t", mappedTo=0, **kwargs).kind == "text"


def test_category_model_rejects_invalid_options():
    """Validates category requires options and defaultValue membership."""
    with pytest.raises(ValidationError):
        CategoryField(label="c", mappedTo=0, options=[])
    with pytest.raises(ValidationError):
        CategoryField(label="c", mappedTo=0, options=["a"], defaultValue="b")


@pytest.mark.parametrize(
    "kwargs",
    [
        {"options": ["a"]},
        {"options": ["a", "b"], "defaultValue": "a"},
        {"options": ["", "x"], "defaultValue": ""},
    ],
)
def test_category_model_accepts_valid_options(kwargs):
    """Validates category options and defaultValue success cases."""
    assert CategoryField(label="c", mappedTo=0, **kwargs).kind == "category"


def test_onehot_category_model_rejects_invalid_option_targets():
    """Validates onehot-category options require concrete backend targets."""
    with pytest.raises(ValidationError):
        OneHotCategoryField(
            label="color",
            options=[{"label": "Red", "value": "red", "mappedTo": ""}],
        )
    with pytest.raises(ValidationError):
        OneHotCategoryField(
            label="color",
            options=[{"label": "Red", "value": "red", "mappedTo": -1}],
        )


@pytest.mark.parametrize(
    "kwargs",
    [
        {"min": "2024-02-01", "max": "2024-01-01"},
        {"min": "2024-02-01", "defaultValue": "2024-01-01"},
        {"max": "2024-01-01", "defaultValue": "2024-02-01"},
        {"step": 0},
    ],
)
def test_date_model_rejects_invalid_constraints(kwargs):
    """Validates date range/defaultValue/step exceptions."""
    with pytest.raises(ValidationError):
        DateField(label="d", mappedTo=0, **kwargs)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"min": "2024-01-01"},
        {"max": "2024-12-31"},
        {"step": 1},
        {"defaultValue": "2024-06-01"},
        {"min": "2024-01-01", "max": "2024-12-31", "defaultValue": "2024-06-01"},
    ],
)
def test_date_model_accepts_optional_attributes(kwargs):
    """Validates date optional attributes and valid date constraints."""
    assert DateField(label="d", mappedTo=0, **kwargs).kind == "date"


def test_series_model_rejects_invalid_subfields_and_point_ranges():
    """Validates series nesting, unknown sub-kind, and point range exceptions."""
    with pytest.raises(ValidationError):
        SeriesField(
            label="s",
            mappedTo=0,
            field1={"kind": "series", "label": "nested", "mappedTo": 0},
            field2={"kind": "text", "label": "value", "mappedTo": 0},
        )


@pytest.mark.parametrize(
    "kwargs",
    [
        {"minPoints": 1},
        {"maxPoints": 2},
        {"minPoints": 1, "maxPoints": 2},
    ],
)
def test_series_model_accepts_valid_point_constraints(kwargs):
    """Validates series point constraints success cases."""
    field = SeriesField(
        label="s",
        mappedTo=0,
        field1={"kind": "text", "label": "x", "mappedTo": 0},
        field2={"kind": "number", "label": "y", "mappedTo": 0, "step": 1},
        **kwargs,
    )

    assert field.kind == "series"
    with pytest.raises(ValidationError):
        SeriesField(
            label="s",
            mappedTo=0,
            field1={"kind": "unknown", "label": "x", "mappedTo": 0},
            field2={"kind": "text", "label": "value", "mappedTo": 0},
        )
    with pytest.raises(ValidationError):
        SeriesField(
            label="s",
            mappedTo=0,
            field1={"kind": "text", "label": "x", "mappedTo": 0},
            field2={"kind": "text", "label": "y", "mappedTo": 0},
            minPoints=2,
            maxPoints=1,
        )
