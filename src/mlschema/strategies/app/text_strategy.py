"""mlschema.strategies.app.text_strategy
=======================================
Inference strategy for **text** columns.

Does not provide additional attributes to the schema: its purpose is solely
to classify the field as ``"text"`` when the series ``dtype`` is
``"object"`` or pandas' new ``"string"`` string.
"""

from __future__ import annotations

from mlschema.core.app.field_strategy import FieldStrategy
from mlschema.strategies.domain import FieldTypes, TextField


class TextStrategy(FieldStrategy):
    """Specific strategy for text fields."""

    def __init__(self) -> None:
        super().__init__(
            type_name=FieldTypes.TEXT,
            schema_cls=TextField,
            dtypes=("object", "string"),
        )
