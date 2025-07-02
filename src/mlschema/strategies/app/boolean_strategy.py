"""mlschema.strategies.app.boolean_strategy
==========================================
Estrategia de inferencia para columnas **booleanas**.

La clase :class:`BooleanStrategy` es una implementación concreta de
:class:`mlschema.core.app.field_strategy.FieldStrategy` que cubre los
``dtype`` de pandas/NumPy ``"bool"`` y ``"boolean"``. No requiere
atributos adicionales, por lo que delega en la clase base la generación
del *schema* estándar.

Ejemplo mínimo
--------------
>>> import pandas as pd
>>> from mlschema.strategies.app.boolean_strategy import BooleanStrategy
>>> s = pd.Series([True, False, True], name="activo", dtype="bool")
>>> BooleanStrategy().build_dict(s)
'{"title":"activo","required":false,"description":null,"type":"boolean"}'
"""

from __future__ import annotations

from mlschema.core.app.field_strategy import FieldStrategy
from mlschema.strategies.domain import BooleanField, FieldTypes


class BooleanStrategy(FieldStrategy):
    """Estrategia específica para campos booleanos."""

    def __init__(self) -> None:
        super().__init__(
            type_name=FieldTypes.BOOLEAN,
            schema_cls=BooleanField,
            dtypes=("bool", "boolean"),
        )
