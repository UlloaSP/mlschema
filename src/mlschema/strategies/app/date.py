# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
"""Date field inference.

The date builder recognises pandas datetime dtype names supported by MLSchema
and emits the builtin `date` field contract. Date constraints such as `min`,
`max`, and `step` remain explicit overrides rather than inferred values.
"""

from __future__ import annotations

from pandas import Series

from mlschema.core.app.kind import FieldContext, FieldDict
from mlschema.strategies.app._base import base_field
from mlschema.strategies.domain import FieldTypes

DATE_DTYPES = {"datetime64[ns]", "datetime64[us]", "datetime64"}


def date_builder(_series: Series, ctx: FieldContext) -> FieldDict | None:
    """Infer a date field for pandas datetime columns.

    Args:
        _series: Source column. The value is unused because dtype metadata in
            `ctx` is sufficient for date inference.
        ctx: Column metadata including normalised dtype, name, and required flag.

    Returns:
        A strict field dict for `DateField` when `ctx.dtype` is a supported
        datetime dtype; otherwise `None`.
    """
    if ctx.dtype not in DATE_DTYPES:
        return None
    return base_field(ctx, FieldTypes.DATE)
