"""
mlschema.core.app.field_service

High-level service that converts a pandas.DataFrame into the JSON payload required by the front-end.

The front-end expects a structure in the following format:

    {
        "input": [
            {"title": "age", "type": "number", ...},
            {"title": "name", "type": "text",   ...},
            ...
        ]
    }

The FieldService class delegates the responsibility of constructing each object in the list to strategies provided by a FieldRegistry.

Example of complete flow:
    ```python
    import pandas as pd
    from mlschema.core import FieldStrategy, BaseField

    class DummyStrategy(FieldStrategy):
        def __init__(self):
            super().__init__(
                type_name="text",
                schema_cls=BaseField,  # Minimal fictitious type
                dtypes=("object",),
            )

    df = pd.DataFrame({"name": ["Ana", "Luis"]})

    service = FieldService()
    service.register(DummyStrategy())
    service.build_schema_from_dataframe(df)
    # Output: '{"input":[{"title":"name","required":false,"description":null,"type":"text"}]};'
    ```
"""

from __future__ import annotations

from json import dumps as json_dumps
from typing import Dict, List

from pandas import DataFrame, Series

from .field_strategy import FieldStrategy
from mlschema.core.app.field_registry import FieldRegistry


class FieldService:
    """Traduce un :class:`~pandas.DataFrame` a la *spec* JSON consumida por el front.

    Parameters
    ----------
    registry:
        Instancia pre‑cargada de :class:`FieldRegistry` que resuelve la
        estrategia apropiada para cada columna.
    """

    def __init__(self) -> None:
        self._registry = FieldRegistry()

    def register(self, strategy: FieldStrategy) -> None:
        """Registra una nueva estrategia de campo.

        Parameters
        ----------
        strategy:
            Instancia de :class:`FieldStrategy` a registrar.
        """
        self._registry.register(strategy)

    def register_all(self, strategies: List[FieldStrategy]) -> None:
        """Registra múltiples estrategias de campo.

        Parameters
        ----------
        strategies:
            Secuencia de instancias de :class:`FieldStrategy` a registrar.
        """
        for strategy in strategies:
            self.register(strategy)

    def unregister(self, strategy: FieldStrategy) -> None:
        """Desregistra una estrategia previamente registrada.

        Parameters
        ----------
        strategy:
            Instancia de :class:`FieldStrategy` a desregistrar.
        """
        self._registry.unregister(strategy)

    def update(self, strategy: FieldStrategy) -> None:
        """Actualiza una estrategia ya registrada.

        Si la estrategia no existe, se registra como nueva.

        Parameters
        ----------
        strategy:
            Instancia de :class:`FieldStrategy` a actualizar.
        """
        self._registry.update(strategy)

    # ------------------------------------------------------------------ #
    # Helpers internos                                                   #
    # ------------------------------------------------------------------ #
    def _field_payload(self, series: Series) -> Dict:
        """Genera el schema para una columna concreta.

        Si el *dtype* de la serie no está asociado a ninguna estrategia,
        se intenta una de reserva bajo el ``type_name`` "text".

        Parameters
        ----------
        series:
            Serie de pandas a inspeccionar.

        Returns
        -------
        dict
            Diccionario con el schema de la columna.

        Raises
        ------
        RuntimeError
            Si no existe estrategia de reserva.
        """
        strat = self._registry.strategy_for_dtype(
            series.dtype
        ) or self._registry.strategy_for_name("text")
        if strat is None:
            raise RuntimeError("No hay estrategia de fallback 'text' registrada.")
        return strat.build_dict(series)

    # ------------------------------------------------------------------ #
    # API pública                                                        #
    # ------------------------------------------------------------------ #
    def _schema_payload(self, df: DataFrame) -> List[Dict]:
        """Construye la lista de schemas para cada columna.

        Parameters
        ----------
        df:
            DataFrame de origen.

        Returns
        -------
        list[dict]
            Lista ordenada de schemas.

        Raises
        ------
        ValueError
            Si el DataFrame no contiene columnas.
        """
        if df.empty:
            raise ValueError("El DataFrame no contiene columnas.")
        return [self._field_payload(df[col]) for col in df.columns]

    def build(self, df: DataFrame) -> str:
        """Devuelve el *payload* final listo para inyección en el front‑end.

        Parameters
        ----------
        df:
            DataFrame a convertir.

        Returns
        -------
        str
            Cadena JSON terminada en ';' conforme al contrato del front.
        """
        raw = json_dumps({"input": self._schema_payload(df)})
        # Limpieza mínima para adaptar al front (compatibilidad histórica)
        return (
            raw.replace('\\"', '"')
            .replace('"{', "{")
            .replace('}"', "}")
            .replace("null", "undefined")
        )
