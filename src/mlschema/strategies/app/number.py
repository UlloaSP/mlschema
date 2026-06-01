# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
"""Numeric field inference.

This module maps supported integer and float pandas dtypes to the builtin
`number` field model. It preserves the previous step rule: integers use `1`,
floats use `0.1`.
"""

from __future__ import annotations

from pandas import Series, api

from mlschema.core.app.kind import FieldContext, FieldDict
from mlschema.strategies.app._base import base_field
from mlschema.strategies.domain import FieldTypes

NUMBER_DTYPES = {"int64", "float64", "int32", "float32"}


def number_builder(series: Series, ctx: FieldContext) -> FieldDict | None:
    """Infer a number field for supported numeric columns.

    Args:
        series: Source column inspected with pandas' dtype helpers to decide the
            generated `step`.
        ctx: Column metadata including normalised dtype, name, and required flag.

    Returns:
        A strict field dict for `NumberField` when `ctx.dtype` is supported;
        otherwise `None`.
    """
    if ctx.dtype not in NUMBER_DTYPES:
        return None
    step = 0.1 if api.types.is_float_dtype(series.dtype) else 1
    return {**base_field(ctx, FieldTypes.NUMBER), "step": step}
