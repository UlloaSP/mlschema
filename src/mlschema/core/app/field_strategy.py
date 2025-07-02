"""
FieldStrategy
================================
Estrategias para derivar metadatos de una columna (``pandas.Series``) y
materializarlos en un *schema* Pydantic.

La clase :class:`FieldStrategy` sirve como clase base para estrategias
específicas de tipo de dato (número, texto, fecha, etc.). Cada estrategia
define:

* ``type_name``  – Identificador lógico del tipo (``"number"``, ``"text"``, …).
* ``schema_cls`` – Subclase de :class:`mlschema.core.domain.BaseField`
  utilizada para serializar el resultado.
* ``dtypes``     – Conjunto de *dtype* de NumPy / pandas para los que la
  estrategia es válida.

Ejemplo de uso
--------------
>>> import pandas as pd
>>> from mlschema.core.domain import NumberField
>>> class NumberStrategy(FieldStrategy):
...     def __init__(self) -> None:
...         super().__init__(
...             type_name="number",
...             schema_cls=NumberField,
...             dtypes=("float64", "int64"),
...         )
...
...     def attributes_from_series(self, series: pd.Series) -> dict:
...         'Deriva atributos básicos: mínimo y máximo.'
...         return {"min": float(series.min()), "max": float(series.max())}
>>> s = pd.Series([1, 2, 3], name="edad", dtype="int64")
>>> NumberStrategy().build_dict(s)
'{"title":"edad","required":true,"description":null,"type":"number","min":1.0,"max":3.0}'
"""

from __future__ import annotations

from collections.abc import Sequence

from numpy import dtype as np_dtype
from pandas import Series, api

from mlschema.core.domain import BaseField


class FieldStrategy:
    """Contrato base para todas las estrategias de campo.

    Cada subclase debe (opcionalmente) sobreescribir
    :meth:`attributes_from_series` para añadir metadatos específicos al
    *schema* generado.

    Attributes
    ----------
    _type_name:
        Identificador lógico del tipo de campo.
    _schema_cls:
        Subclase de :class:`BaseField` utilizada para la serialización.
    _dtypes:
        *Tuple* de nombres de ``dtype`` compatibles con la estrategia.
    """

    # -------------------------- construcción --------------------------- #
    def __init__(
        self,
        *,
        type_name: str,
        schema_cls: type[BaseField],
        dtypes: Sequence[str | np_dtype],
    ) -> None:
        """Inicializa la estrategia.

        Parameters
        ----------
        type_name:
            Identificador lógico del tipo (p. ej. ``"number"``).
        schema_cls:
            Clase Pydantic que modeliza el campo.
        dtypes:
            Secuencia de ``dtype`` (instancias o nombres) a los que se aplica la estrategia.
        """
        self._type_name: str = type_name
        self._schema_cls: type[BaseField] = schema_cls
        # Normalizamos los dtype a ``str`` para comparaciones futuras
        self._dtypes: tuple[str, ...] = tuple(
            dt.name
            if isinstance(dt, np_dtype | api.extensions.ExtensionDtype)
            else str(dt)
            for dt in dtypes
        )

    # -------------------------- properties ----------------------------- #
    @property
    def type_name(self) -> str:
        """Nombre lógico del tipo de campo."""
        return self._type_name

    @property
    def schema_cls(self) -> type[BaseField]:
        """Clase Pydantic utilizada para serializar el schema."""
        return self._schema_cls

    @property
    def dtypes(self) -> tuple[str, ...]:
        """Tupla de nombres de ``dtype`` soportados."""
        return self._dtypes

    # -------------------- punto de extensión opcional ----------------- #
    def attributes_from_series(self, series: Series) -> dict:
        """Calcula los atributos específicos del campo.

        Este método puede ser sobreescrito en cada estrategia concreta
        para derivar atributos como ``min``, ``max``, ``options``, etc.

        Parameters
        ----------
        series:
            Columna de pandas a analizar.

        Returns
        -------
        dict
            Diccionario con atributos adicionales; nunca incluye las claves
            estándar ``title``, ``required``, ``description`` o ``type``.
        """
        return {}

    # -------------------- fabricador de payload completo --------------- #
    def build_dict(self, series: Series) -> str:
        """Crea la representación JSON del schema.

        Combina los atributos estándar con los devueltos por
        :meth:`attributes_from_series` y serializa el resultado con la
        clase Pydantic asociada.

        Parameters
        ----------
        series:
            Columna de pandas a documentar.

        Returns
        -------
        str
            Cadena JSON con el schema del campo.
        """
        base_attrs: dict = {
            "title": series.name,
            "required": series.notnull().all(),
            "description": None,
            "type": self.type_name,
        }
        # Incorporar atributos específicos de la implementación
        base_attrs.update(self.attributes_from_series(series))

        # Instanciar la clase Pydantic y volcar a JSON
        return self._schema_cls(**base_attrs).model_dump_json()
