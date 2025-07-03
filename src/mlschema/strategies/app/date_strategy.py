"""mlschema.strategies.app.date_strategy
=======================================
Inference strategy for **date** columns.

This concrete implementation of
:class:`mlschema.core.app.field_strategy.FieldStrategy` covers the classic
pandas/NumPy ``dtype`` ``"datetime64[ns]"`` and ``"datetime64"``.
It does not add specific attributes; it simply delegates to the base class
the construction of the standard *schema*.
"""

from __future__ import annotations

from mlschema.core.app.field_strategy import FieldStrategy
from mlschema.strategies.domain import DateField, FieldTypes


class DateStrategy(FieldStrategy):
    """Specific strategy for date fields."""

    def __init__(self) -> None:
        super().__init__(
            type_name=FieldTypes.DATE,
            schema_cls=DateField,
            dtypes=("datetime64[ns]", "datetime64"),
        )
