# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
"""Empty DataFrame inference error."""

from __future__ import annotations

from pandas import DataFrame

from mlschema.core.exceptions.field_service import FieldServiceError


class EmptyDataFrameError(FieldServiceError):
    """Raised when inference receives a DataFrame with no rows or columns.

    Args:
        df: DataFrame that failed the minimum shape requirement.

    Attributes:
        param: Always `"dataframe"`.
        value: The invalid DataFrame.
        context: Row and column counts at failure time.
    """

    def __init__(self, df: DataFrame) -> None:
        super().__init__(
            param="dataframe",
            value=df,
            message="DataFrame contains no columns or rows.",
            context={"rows": len(df.index), "cols": len(df.columns)},
        )
