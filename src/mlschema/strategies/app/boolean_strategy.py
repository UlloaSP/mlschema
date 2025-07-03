"""mlschema.strategies.app.boolean_strategy
==========================================
Inference strategy for **boolean** columns.

The :class:`BooleanStrategy` class is a concrete implementation of
:class:`mlschema.core.app.field_strategy.FieldStrategy` that covers the
pandas/NumPy ``dtype`` ``"bool"`` and ``"boolean"``. It does not require
additional attributes, so it delegates to the base class the generation
of the standard *schema*.

"""

from __future__ import annotations

from mlschema.core.app.field_strategy import FieldStrategy
from mlschema.strategies.domain import BooleanField, FieldTypes


class BooleanStrategy(FieldStrategy):
    """Specific strategy for boolean fields."""

    def __init__(self) -> None:
        super().__init__(
            type_name=FieldTypes.BOOLEAN,
            schema_cls=BooleanField,
            dtypes=("bool", "boolean"),
        )
