"""mlschema.strategies.app.date_strategy
=======================================
Estrategia de inferencia para columnas **fecha/hora**.

Esta implementación concreta de
:class:`mlschema.core.app.field_strategy.FieldStrategy` cubre los ``dtype``
clásicos de pandas/NumPy ``"datetime64[ns]"`` y ``"datetime64"``.
No añade atributos específicos; simplemente delega en la clase base la
construcción del *schema* estándar.

Ejemplo mínimo
--------------
>>> import pandas as pd
>>> from mlschema.strategies.app.date_strategy import DateStrategy
>>> s = pd.Series(pd.date_range("2024-01-01", periods=3), name="fecha")
>>> DateStrategy().build_dict(s)
'{"title":"fecha","required":true,"description":null,"type":"date"}'
"""

from __future__ import annotations

from mlschema.core.app.field_strategy import FieldStrategy
from mlschema.strategies.domain import DateField, FieldTypes


class DateStrategy(FieldStrategy):
    """Estrategia específica para campos de fecha/hora."""

    def __init__(self) -> None:
        super().__init__(
            type_name=FieldTypes.DATE,
            schema_cls=DateField,
            dtypes=("datetime64[ns]", "datetime64"),
        )
