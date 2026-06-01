# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
"""Boolean field inference.

The builder in this module maps pandas boolean dtypes to the builtin
`boolean` field model. It emits only the common field attributes because
`BooleanField` carries no data-derived attributes beyond nullability.
"""

from __future__ import annotations

from pandas import Series

from mlschema.core.app.kind import FieldContext, FieldDict
from mlschema.strategies.app._base import base_field
from mlschema.strategies.domain import FieldTypes


def boolean_builder(_series: Series, ctx: FieldContext) -> FieldDict | None:
    """Infer a boolean field for pandas boolean columns.

    Args:
        _series: Source column. The value is unused because dtype metadata in
            `ctx` is sufficient for boolean inference.
        ctx: Column metadata including normalised dtype, name, and required flag.

    Returns:
        A strict field dict for `BooleanField` when `ctx.dtype` is `bool` or
        `boolean`; otherwise `None` so the next builder can try.
    """
    if ctx.dtype not in {"bool", "boolean"}:
        return None
    return base_field(ctx, FieldTypes.BOOLEAN)
