"""mlschema.strategies.app.number_strategy
=========================================
Estrategia de inferencia para columnas **numéricas**.

Deriva metadatos adicionales aptos para campos de entrada de tipo número.
Concretamente, calcula el atributo ``step`` que el front-end utilizará
como incremento por defecto en controles ``<input type="number">``.

Reglas de negocio
-----------------
* Para ``float`` → ``step = 0.1``.
* Para ``int``   → ``step = 1``.

Ejemplo de uso
--------------
>>> import pandas as pd
>>> from mlschema.strategies.app.number_strategy import NumberStrategy
>>> s = pd.Series([1, 2, 3], name="edad", dtype="int64")
>>> NumberStrategy().build_dict(s)
'{"title":"edad","required":true,"description":null,"type":"number","step":1}'
"""

from __future__ import annotations

from pandas import Series, api

from mlschema.core.app.field_strategy import FieldStrategy
from mlschema.strategies.domain import FieldTypes, NumberField


class NumberStrategy(FieldStrategy):
    """Estrategia para columnas numéricas (enteras y flotantes)."""

    def __init__(self) -> None:
        super().__init__(
            type_name=FieldTypes.NUMBER,
            schema_cls=NumberField,
            dtypes=("int64", "float64", "int32", "float32"),
        )

    # ------------------------------------------------------------------ #
    # Métodos específicos                                                #
    # ------------------------------------------------------------------ #
    def attributes_from_series(self, series: Series) -> dict:
        """Deriva el atributo ``step`` a partir del ``dtype``.

        Parameters
        ----------
        series:
            Serie de pandas con valores numéricos.

        Returns
        -------
        dict
            Diccionario con la clave ``step``.
        """
        # Paso por defecto: 0.1 para floats, 1 para enteros
        step = 0.1 if api.types.is_float_dtype(series.dtype) else 1
        return {"step": step}
