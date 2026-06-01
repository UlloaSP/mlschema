# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
"""Text fallback inference.

Text is the final builtin builder. It intentionally accepts every column that
earlier builders did not claim, providing deterministic fallback behaviour for
unknown or mixed object dtypes.
"""

from __future__ import annotations

from pandas import Series

from mlschema.core.app.kind import FieldContext, FieldDict
from mlschema.strategies.app._base import base_field
from mlschema.strategies.domain import FieldTypes


def text_builder(_series: Series, ctx: FieldContext) -> FieldDict:
    """Infer a text field for any remaining column.

    Args:
        _series: Source column. The value is unused because this builder is a
            fallback and accepts any dtype not claimed earlier.
        ctx: Column metadata including name and required flag.

    Returns:
        A strict field dict for `TextField`.
    """
    return base_field(ctx, FieldTypes.TEXT)
