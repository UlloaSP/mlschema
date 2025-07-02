"""mlschema.strategies.app.category_strategy
===========================================
Estrategia de inferencia para columnas **categóricas**.

Esta implementación concreta de :class:`mlschema.core.app.field_strategy.FieldStrategy`
extrae el conjunto de valores distintos presentes en la serie y los
publica en el atributo ``options`` del schema.

- Si la columna ya es de tipo ``CategoricalDtype`` se respetan las
  categorías definidas.
- En caso contrario, se construye la lista a partir de los valores únicos
  no nulos.

Ejemplo de uso
--------------
>>> import pandas as pd
>>> from mlschema.strategies.app.category_strategy import CategoryStrategy
>>> s = pd.Series(["A", "B", "A"], name="color", dtype="object")
>>> CategoryStrategy().build_dict(s)
'{"title":"color","required":false,"description":null,"type":"category","options":["A","B"]}'
"""

from __future__ import annotations

from pandas import CategoricalDtype, Series

from mlschema.core.app.field_strategy import FieldStrategy
from mlschema.strategies.domain import CategoryField, FieldTypes

__all__ = ["CategoryStrategy"]


class CategoryStrategy(FieldStrategy):
    """Estrategia para columnas categóricas."""

    def __init__(self) -> None:
        super().__init__(
            type_name=FieldTypes.CATEGORY,
            schema_cls=CategoryField,
            dtypes=("category",),
        )

    # ------------------------------------------------------------------ #
    # Métodos específicos                                                #
    # ------------------------------------------------------------------ #
    def attributes_from_series(self, series: Series) -> dict:
        """Deriva la lista de *options* a partir de la serie.

        Parameters
        ----------
        series:
            Serie de pandas con valores categóricos.

        Returns
        -------
        dict
            Diccionario con la clave ``options`` y la lista de valores
            únicos.
        """
        if isinstance(series.dtype, CategoricalDtype):
            options = list(series.cat.categories)
        else:
            options = list(series.dropna().unique())
        return {"options": options}
