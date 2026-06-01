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
    SeriesField,
    TextField,
)


def test_builtin_models_accept_valid_success_cases():
    """Validates every builtin field model accepts a representative valid field."""
    BooleanField(label="flag", defaultValue=True, trueLabel="yes", falseLabel="no")
    CategoryField(label="tier", options=["free", "pro"], defaultValue="pro")
    DateField(label="start", min="2024-01-01", max="2024-12-31", step=1)
    NumberField(label="score", min=0, max=100, defaultValue=50, step=1)
    TextField(label="name", minLength=1, maxLength=20, defaultValue="Ada")
    SeriesField(
        label="readings",
        field1={"kind": "text", "label": "x"},
        field2={"kind": "number", "label": "y", "step": 1},
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
    assert BooleanField(**kwargs).kind == "boolean"


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
        NumberField(label="n", **kwargs)


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
    assert NumberField(label="n", **kwargs).kind == "number"


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
        TextField(label="t", **kwargs)


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
    assert TextField(label="t", **kwargs).kind == "text"


def test_category_model_rejects_invalid_options():
    """Validates category requires options and defaultValue membership."""
    with pytest.raises(ValidationError):
        CategoryField(label="c", options=[])
    with pytest.raises(ValidationError):
        CategoryField(label="c", options=["a"], defaultValue="b")


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
    assert CategoryField(label="c", **kwargs).kind == "category"


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
        DateField(label="d", **kwargs)


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
    assert DateField(label="d", **kwargs).kind == "date"


def test_series_model_rejects_invalid_subfields_and_point_ranges():
    """Validates series nesting, unknown sub-kind, and point range exceptions."""
    with pytest.raises(ValidationError):
        SeriesField(
            label="s",
            field1={"kind": "series", "label": "nested"},
            field2={"kind": "text", "label": "value"},
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
        field1={"kind": "text", "label": "x"},
        field2={"kind": "number", "label": "y", "step": 1},
        **kwargs,
    )

    assert field.kind == "series"
    with pytest.raises(ValidationError):
        SeriesField(
            label="s",
            field1={"kind": "unknown", "label": "x"},
            field2={"kind": "text", "label": "value"},
        )
    with pytest.raises(ValidationError):
        SeriesField(
            label="s",
            field1={"kind": "text", "label": "x"},
            field2={"kind": "text", "label": "y"},
            minPoints=2,
            maxPoints=1,
        )
