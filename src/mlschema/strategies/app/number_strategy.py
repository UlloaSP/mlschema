"""mlschema.strategies.app.number_strategy
=========================================
Inference strategy for **numeric** columns.

Derives additional metadata suitable for number input fields.
Specifically, calculates the ``step`` attribute that the front-end will use
as the default increment in ``<input type="number">`` controls.

Business rules
--------------
* For ``float`` → ``step = 0.1``.
* For ``int``   → ``step = 1``.

"""

from __future__ import annotations

from pandas import Series, api

from mlschema.core.app.field_strategy import FieldStrategy
from mlschema.strategies.domain import FieldTypes, NumberField


class NumberStrategy(FieldStrategy):
    """Strategy for numeric columns."""

    def __init__(self) -> None:
        super().__init__(
            type_name=FieldTypes.NUMBER,
            schema_cls=NumberField,
            dtypes=("int64", "float64", "int32", "float32"),
        )

    def attributes_from_series(self, series: Series) -> dict:
        """Derives the ``step`` attribute from the ``dtype``.

        Parameters
        ----------
        series:
            Pandas series with numeric values.

        Returns
        -------
        dict
            Dictionary with the ``step`` key.
        """
        # Default step: 0.1 for floats, 1 for integers
        step = 0.1 if api.types.is_float_dtype(series.dtype) else 1
        return {"step": step}
