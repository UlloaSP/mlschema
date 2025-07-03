"""mlschema.strategies.app.category_strategy
===========================================
Inference strategy for **categorical** columns.

This concrete implementation of :class:`mlschema.core.app.field_strategy.FieldStrategy`
extracts the set of distinct values present in the series and
publishes them in the ``options`` attribute of the schema.

- If the column is already of type ``CategoricalDtype``, the defined
  categories are respected.
- Otherwise, the list is built from unique non-null values.

"""

from __future__ import annotations

from pandas import CategoricalDtype, Series

from mlschema.core.app.field_strategy import FieldStrategy
from mlschema.strategies.domain import CategoryField, FieldTypes


class CategoryStrategy(FieldStrategy):
    """Strategy for categorical columns."""

    def __init__(self) -> None:
        super().__init__(
            type_name=FieldTypes.CATEGORY,
            schema_cls=CategoryField,
            dtypes=("category",),
        )

    def attributes_from_series(self, series: Series) -> dict:
        """Derives the list of *options* from the series.

        Parameters
        ----------
        series:
            Pandas series with categorical values.

        Returns
        -------
        dict
            Dictionary with the ``options`` key and the list of unique
            values.
        """
        if isinstance(series.dtype, CategoricalDtype):
            options = list(series.cat.categories)
        else:
            options = list(series.dropna().unique())
        return {"options": options}
