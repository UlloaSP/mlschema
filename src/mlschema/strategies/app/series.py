# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
"""Two-axis series field inference.

The series builder claims columns whose non-null cells are two-element tuples,
lists, or dictionaries. It splits each cell into two sub-series and delegates
sub-field inference back to the active inference pipeline via
`FieldContext.infer_field`.
"""

from __future__ import annotations

import datetime

import pandas as pd
from pandas import Series

from mlschema.core.app.kind import FieldContext, FieldDict
from mlschema.strategies.app._base import base_field
from mlschema.strategies.domain import FieldTypes


def series_builder(series: Series, ctx: FieldContext) -> FieldDict | None:
    """Infer a series field for columns containing two-element cells.

    Args:
        series: Source column containing tuple, list, or dict cells.
        ctx: Column metadata plus the recursive `infer_field` callback used for
            sub-field inference.

    Returns:
        A strict field dict for `SeriesField` when all non-null cells are
        two-element compound values; otherwise `None`.
    """
    non_null = series.dropna()
    if len(non_null) == 0:
        return None
    if not all(_is_pair(value) for value in non_null):
        return None
    field1, field2 = _extract_sub_series(non_null)
    return {
        **base_field(ctx, FieldTypes.SERIES),
        "field1": ctx.infer_field(_coerce_sub_series(field1)),
        "field2": ctx.infer_field(_coerce_sub_series(field2)),
    }


def _is_pair(value: object) -> bool:
    return (isinstance(value, (list, tuple)) and len(value) == 2) or (
        isinstance(value, dict) and len(value) == 2
    )


def _extract_sub_series(series: Series) -> tuple[Series, Series]:
    first = series.iloc[0]
    if isinstance(first, dict):
        keys = list(first.keys())
        return (
            pd.Series([value[keys[0]] for value in series], name=str(keys[0])),
            pd.Series([value[keys[1]] for value in series], name=str(keys[1])),
        )
    return (
        pd.Series([value[0] for value in series], name="field1"),
        pd.Series([value[1] for value in series], name="field2"),
    )


def _coerce_sub_series(series: Series) -> Series:
    if series.dtype != object:
        return series
    non_null = series.dropna()
    all_dates = bool(
        non_null.apply(
            lambda value: isinstance(value, (datetime.date, datetime.datetime))
        ).all()
    )
    if all_dates:
        return pd.Series(pd.to_datetime(series), name=series.name)
    try:
        return pd.Series(pd.to_datetime(series, format="mixed"), name=series.name)
    except ValueError, TypeError:
        pass
    coerced = pd.Series(pd.to_numeric(series, errors="coerce"), name=series.name)
    if not bool(coerced.isna().all()):
        return coerced
    return series
