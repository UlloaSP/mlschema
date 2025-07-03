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

from pandas import DataFrame, Series

from mlschema.core.app.field_registry import FieldRegistry

from .field_strategy import FieldStrategy


class FieldService:
    """Translates a :class:`~pandas.DataFrame` to the JSON spec consumed by the front-end.

    Parameters
    ----------
    registry:
        Pre-loaded instance of :class:`FieldRegistry` that resolves the
        appropriate strategy for each column.
    """

    def __init__(self) -> None:
        self._registry = FieldRegistry()

    def register(self, strategy: FieldStrategy) -> None:
        """Register a new field strategy.

        Parameters
        ----------
        strategy:
            Instance of :class:`FieldStrategy` to register.
        """
        self._registry.register(strategy)

    def register_all(self, strategies: list[FieldStrategy]) -> None:
        """Register multiple field strategies.

        Parameters
        ----------
        strategies:
            Sequence of :class:`FieldStrategy` instances to register.
        """
        for strategy in strategies:
            self.register(strategy)

    def unregister(self, strategy: FieldStrategy) -> None:
        """Unregister a previously registered strategy.

        Parameters
        ----------
        strategy:
            Instance of :class:`FieldStrategy` to unregister.
        """
        self._registry.unregister(strategy.type_name)

    def update(self, strategy: FieldStrategy) -> None:
        """Update an already registered strategy.

        If the strategy doesn't exist, it's registered as new.

        Parameters
        ----------
        strategy:
            Instance of :class:`FieldStrategy` to update.
        """
        self._registry.update(strategy)

    # ------------------------------------------------------------------ #
    # Internal helpers                                                   #
    # ------------------------------------------------------------------ #
    def _field_payload(self, series: Series) -> str:
        """Generate the schema for a specific column.

        If the series dtype is not associated with any strategy,
        a fallback strategy under the ``type_name`` "text" is attempted.

        Parameters
        ----------
        series:
            Pandas series to inspect.

        Returns
        -------
        str
            JSON string with the column schema.

        Raises
        ------
        RuntimeError
            If no fallback strategy exists.
        """
        strat = self._registry.strategy_for_dtype(
            str(series.dtype)
        ) or self._registry.strategy_for_name("text")
        if strat is None:
            raise RuntimeError("No fallback 'text' strategy registered.")
        return strat.build_dict(series)

    # ------------------------------------------------------------------ #
    # Public API                                                         #
    # ------------------------------------------------------------------ #
    def _schema_payload(self, df: DataFrame) -> list[str]:
        """Build the list of schemas for each column.

        Parameters
        ----------
        df:
            Source DataFrame.

        Returns
        -------
        list[str]
            Ordered list of schemas.

        Raises
        ------
        ValueError
            If the DataFrame contains no columns.
        """
        if df.empty:
            raise ValueError("DataFrame contains no columns.")
        return [self._field_payload(df.iloc[:, i]) for i, _ in enumerate(df.columns)]

    def build(self, df: DataFrame) -> str:
        """Return the final payload ready for injection into the front-end.

        Parameters
        ----------
        df:
            DataFrame to convert.

        Returns
        -------
        str
            JSON string ending in ';' conforming to the front-end contract.
        """
        raw = json_dumps({"input": self._schema_payload(df)})
        # Minimal cleanup to adapt to front-end (historical compatibility)
        return (
            raw.replace('\\"', '"')
            .replace('"{', "{")
            .replace('}"', "}")
            .replace("null", "undefined")
        )
