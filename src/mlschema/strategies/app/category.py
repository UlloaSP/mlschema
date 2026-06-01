# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
"""Categorical field inference.

This module owns the builtin `category` inference rules. Categorical pandas
columns preserve declared category order and unused categories; non-categorical
series passed directly to the builder are handled defensively by extracting
non-null unique values.
"""

from __future__ import annotations

from pandas import CategoricalDtype, Series

from mlschema.core.app.kind import FieldContext, FieldDict
from mlschema.strategies.app._base import base_field
from mlschema.strategies.domain import FieldTypes


def category_builder(series: Series, ctx: FieldContext) -> FieldDict | None:
    """Infer a category field from a pandas categorical column.

    Args:
        series: Source column whose options are extracted from categorical
            metadata or non-null unique values.
        ctx: Column metadata including normalised dtype, name, and required flag.

    Returns:
        A strict field dict for `CategoryField` when `ctx.dtype` is `category`;
        otherwise `None`.
    """
    if ctx.dtype != "category":
        return None
    if isinstance(series.dtype, CategoricalDtype):
        options = list(series.cat.categories)
    else:
        options = list(series.dropna().unique())
    return {**base_field(ctx, FieldTypes.CATEGORY), "options": options}
