# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
from __future__ import annotations

from pandas import CategoricalDtype, Series

from mlschema.core import Strategy
from mlschema.strategies.domain import CategoryField, FieldTypes


class CategoryStrategy(Strategy):
    """Instance of Strategy for category fields.

    Name:
        `category`

    Dtypes:
        | Name     | Type              |
        | -------- | ----------------- |
        | category | `CategoricalDtype`|

    Model Attributes:
        | Name    | Type                  | Description                      |
        | ------- | --------------------- | -------------------------------- |
        | kind    | `Literal["category"]` | Fixed type for the strategy.     |
        | options | `list[str]`           | List of allowed categories.      |
        | defaultValue | `str | None`     | Initial value of the field.      |

    Model Restrictions:
        | Description           | Error Type            | Error Message                                     |
        | --------------------- | --------------------- | ------------------------------------------------- |
        | `defaultValue` in `options`  | `PydanticCustomError` | `defaultValue must be in options`      |

    """

    def __init__(self) -> None:
        super().__init__(
            type_name=FieldTypes.CATEGORY,
            schema_cls=CategoryField,
            dtypes=("category",),
        )

    def attributes_from_series(self, series: Series) -> dict:
        """Derives the list of *options* from the series.

        Args:
            series: Pandas series with categorical values.

        Returns:
            Dictionary with the ``options`` key and the list of unique values.
        """
        if isinstance(series.dtype, CategoricalDtype):
            options = list(series.cat.categories)
        else:
            options = list(series.dropna().unique())
        return {"options": options}
