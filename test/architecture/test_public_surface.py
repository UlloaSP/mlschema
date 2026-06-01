# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
from __future__ import annotations

from pathlib import Path

import mlschema
from mlschema.strategies.app import (
    boolean_builder,
    category_builder,
    date_builder,
    number_builder,
    series_builder,
    text_builder,
)

ROOT = Path(__file__).resolve().parents[2]


def test_public_surface_exports_only_function_first_api():
    """Validates public package exports do not expose removed object APIs."""
    exported = set(mlschema.__all__)

    assert {
        "infer_schema",
        "kind",
        "FieldContext",
        "FieldKind",
        "BaseField",
    } <= exported
    assert (
        not {"ML" + "Schema", "Str" + "ategy", "Reg" + "istry", "Ser" + "vice"}
        & exported
    )


def test_builtin_modules_are_split_by_kind():
    """Validates every builtin builder lives in a dedicated kind module."""
    expected = {
        "boolean.py",
        "category.py",
        "date.py",
        "number.py",
        "series.py",
        "text.py",
        "factory.py",
    }
    files = {
        path.name
        for path in (ROOT / "src" / "mlschema" / "strategies" / "app").glob("*.py")
    }

    assert expected <= files
    assert "builtins.py" not in files
    assert all(
        callable(builder)
        for builder in [
            boolean_builder,
            category_builder,
            date_builder,
            number_builder,
            series_builder,
            text_builder,
        ]
    )


def test_strict_exception_modules_are_split_by_failure_mode():
    """Validates strict exception modules are modular, not bundled."""
    files = {
        path.name
        for path in (ROOT / "src" / "mlschema" / "core" / "exceptions").glob("*.py")
    }

    assert {
        "field_kind.py",
        "field_kind_conflict.py",
        "unknown_field_kind.py",
        "field_builder.py",
        "field_service.py",
        "empty_dataframe.py",
    } <= files
    assert "registry.py" not in files
    assert "service.py" not in files


def test_active_source_and_tests_do_not_reference_removed_modules():
    """Validates active source/tests contain no removed-module imports."""
    forbidden = [
        "core.app.reg" + "istry",
        "core.app.str" + "ategy",
        "core.app.ser" + "vice",
    ]
    checked_paths = [
        path
        for folder in [ROOT / "src", ROOT / "test"]
        for path in folder.rglob("*.py")
        if "__pycache__" not in path.parts
    ]

    for path in checked_paths:
        text = path.read_text(encoding="utf-8")
        assert all(item not in text for item in forbidden), path
