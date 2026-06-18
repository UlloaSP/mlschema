# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
"""Factory for builtin field kinds.

The factory keeps the builtin inference order in one place without placing all
builtin inference logic in one module. `infer_schema()` calls `builtin_kinds()`
for every run so callers receive fresh immutable `FieldKind` definitions.
"""

from __future__ import annotations

from mlschema.core.app.kind import FieldKind, kind
from mlschema.strategies.app.boolean import boolean_builder
from mlschema.strategies.app.category import category_builder
from mlschema.strategies.app.date import date_builder
from mlschema.strategies.app.number import number_builder
from mlschema.strategies.app.series import series_builder
from mlschema.strategies.app.text import text_builder
from mlschema.strategies.domain import (
    BooleanField,
    CategoryField,
    DateField,
    NumberField,
    OneHotCategoryField,
    SeriesField,
    TextField,
)


def builtin_kinds() -> tuple[FieldKind, ...]:
    """Return builtin strict field kinds in inference order.

    Returns:
        Tuple of builtin `FieldKind` values ordered from most specific to most
        general. `series` runs before dtype-based builders, and `text` runs last
        as fallback.
    """
    return (
        kind(model=SeriesField, infer=series_builder),
        kind(model=OneHotCategoryField, infer=lambda _series, _ctx: None),
        kind(model=BooleanField, infer=boolean_builder),
        kind(model=CategoryField, infer=category_builder),
        kind(model=DateField, infer=date_builder),
        kind(model=NumberField, infer=number_builder),
        kind(model=TextField, infer=text_builder),
    )
