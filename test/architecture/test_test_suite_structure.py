# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_test_suite_is_split_by_scope():
    """Validates test layout has unit, integration, architecture, and load scopes."""
    test_root = ROOT / "test"

    assert (test_root / "unit").is_dir()
    assert (test_root / "integration").is_dir()
    assert (test_root / "architecture").is_dir()
    assert (test_root / "load").is_dir()


def test_test_files_stay_under_repo_line_limit():
    """Validates test modularity by enforcing the 300-line file limit."""
    for path in (ROOT / "test").rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        line_count = len(path.read_text(encoding="utf-8").splitlines())
        assert line_count <= 300, path


def test_tests_do_not_use_removed_public_class_api():
    """Validates tests have no direct references to removed object API names."""
    forbidden = [
        "ML" + "Schema(",
        "from mlschema import ML" + "Schema",
        "Str" + "ategy(",
        "Reg" + "istry(",
        "Ser" + "vice(",
    ]

    for path in (ROOT / "test").rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        assert all(item not in text for item in forbidden), path
