"""mlschema.strategies.app.text_strategy
=======================================
Estrategia de inferencia para columnas **de texto**.

No aporta atributos adicionales al schema: su cometido es únicamente
clasificar el campo como ``"text"`` cuando el ``dtype`` de la serie es
``"object"`` o la nueva cadena ``"string"`` de pandas.

Ejemplo mínimo
--------------
>>> import pandas as pd
>>> from mlschema.strategies.app.text_strategy import TextStrategy
>>> s = pd.Series(["foo", "bar"], name="comentario", dtype="object")
>>> TextStrategy().build_dict(s)
'{"title":"comentario","required":false,"description":null,"type":"text"}'
"""

from __future__ import annotations

from mlschema.core.app.field_strategy import FieldStrategy
from mlschema.strategies.domain import FieldTypes, TextField


class TextStrategy(FieldStrategy):
    """Estrategia específica para campos de texto."""

    def __init__(self) -> None:
        super().__init__(
            type_name=FieldTypes.TEXT,
            schema_cls=TextField,
            dtypes=("object", "string"),
        )
