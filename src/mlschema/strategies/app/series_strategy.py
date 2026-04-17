# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
from __future__ import annotations

import datetime
from typing import Any

import pandas as pd
from pandas import Series

from mlschema.core import Strategy
from mlschema.strategies.domain import FieldTypes, SeriesField


class SeriesStrategy(Strategy):
    """Strategy for series (two-axis) fields.

    Each cell must be a 2-element compound value:
        - tuple/list: ``(v1, v2)`` — positional, names default to ``"field1"`` / ``"field2"``
        - dict:       ``{"key1": v1, "key2": v2}`` — named, dict keys become sub-field labels

    Field schemas are auto-inferred from sampled cell values via the injected registry.
    No dtypes registered — selected automatically via :meth:`content_probe` or applied manually.

    Name:
        ``series``

    Dtypes:
        None — content-based detection only.

    Model Attributes:
        | Name      | Type                  | Description                               |
        | --------- | --------------------- | ----------------------------------------- |
        | kind      | ``Literal["series"]`` | Fixed type identifier.                    |
        | field1    | ``BaseField``         | Schema of the first element of each cell. |
        | field2    | ``BaseField``         | Schema of the second element of each cell.|

    Model Restrictions:
        | Description                   | Error Type             | Error Message                                                                    |
        | ----------------------------- | ---------------------- | -------------------------------------------------------------------------------- |
        | ``field1/field2`` not series  | ``PydanticCustomError``| ``SeriesField cannot be nested``                                                 |
        | ``field1/field2`` kind known  | ``PydanticCustomError``| ``Unknown sub-field type: '{kind_name}'. Register via add_series_sub_field()``  |

    Note:
        ``minPoints`` and ``maxPoints`` are constraints on :class:`SeriesField` itself and
        must be set there directly — they are not strategy-level parameters.
    """

    def __init__(self) -> None:
        super().__init__(
            type_name=FieldTypes.SERIES,
            schema_cls=SeriesField,
            dtypes=(),
        )
        self._registry: Any = None  # injected by Service via set_registry()

    def set_registry(self, registry: Any) -> None:
        """Store registry reference injected by Service after registration."""
        self._registry = registry

    def content_probe(self, series: Series) -> bool:
        """Return True if all non-null values are 2-element tuples, lists, or dicts.

        Args:
            series: DataFrame column to inspect.

        Returns:
            True if the column contains only 2-element compound values.
        """
        non_null = series.dropna()
        if len(non_null) == 0:
            return False
        return all(
            (isinstance(v, (list, tuple)) and len(v) == 2)
            or (isinstance(v, dict) and len(v) == 2)
            for v in non_null
        )

    def _extract_sub_series(self, series: Series) -> tuple[Series, Series]:
        """Split compound cells into two positional sub-Series.

        Args:
            series: DataFrame column with 2-element compound values.

        Returns:
            Pair of Series — one per element position/key.
        """
        non_null = series.dropna()
        first = non_null.iloc[0]

        if isinstance(first, dict):
            keys = list(first.keys())
            s1 = pd.Series([v[keys[0]] for v in non_null], name=keys[0])
            s2 = pd.Series([v[keys[1]] for v in non_null], name=keys[1])
        else:  # tuple / list
            s1 = pd.Series([v[0] for v in non_null], name="field1")
            s2 = pd.Series([v[1] for v in non_null], name="field2")

        return s1, s2

    def attributes_from_series(self, series: Series) -> dict:
        """Derive ``field1`` and ``field2`` sub-schemas from the series.

        Extracts element sub-Series from compound cells, infers their dtypes via the
        injected registry, and delegates schema building to the matching strategy.
        Falls back to a bare text schema when no registry is available or the dtype
        is unrecognised.

        Args:
            series: DataFrame column with 2-element compound values.

        Returns:
            Dictionary with ``field1`` and ``field2`` sub-schemas.
        """
        s1, s2 = self._extract_sub_series(series)

        def _coerce(s: Series) -> Series:
            """Narrow object-dtype sub-Series: try datetime, then numeric."""
            if s.dtype != object:
                return s
            non_null = s.dropna()
            # Fast-path: all values are Python date/datetime — no format guessing needed
            all_dates: bool = bool(
                non_null.apply(
                    lambda v: isinstance(v, (datetime.date, datetime.datetime))
                ).all()
            )
            if all_dates:
                return pd.Series(pd.to_datetime(s))
            try:
                return pd.Series(pd.to_datetime(s, format="mixed"))
            except (ValueError, TypeError):
                pass
            coerced: Series = pd.Series(pd.to_numeric(s, errors="coerce"))
            if not bool(coerced.isna().all()):
                return coerced
            return s

        def _resolve(s: Series) -> dict:
            s = _coerce(s)
            if self._registry is None:
                return {"kind": "text", "label": str(s.name), "required": True}
            strat = self._registry.strategy_for_dtype(
                s.dtype
            ) or self._registry.strategy_for_name("text")
            if strat is None:
                return {"kind": "text", "label": str(s.name), "required": True}
            return strat.build_dict(s)

        return {"field1": _resolve(s1), "field2": _resolve(s2)}
