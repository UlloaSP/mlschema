from __future__ import annotations

from pandas import DataFrame, Series

from mlschema.core.app.registry import Registry
from mlschema.core.exceptions.service import (
    EmptyDataFrameError,
    FallbackStrategyMissingError,
)
from mlschema.core.util import normalize_dtype

from .strategy import Strategy


class Service:
    """Translates a :class:`pandas.DataFrame` to the JSON spec consumed by the front-end.

    The Service class acts as the main orchestrator for converting pandas DataFrame
    structures into JSON schema payloads. It uses a registry-based strategy pattern
    to handle different data types and their corresponding schema representations.

    The service generates JSON payloads in the format:
    {"inputs": [...], "outputs": [...]}

    Attributes:
        _registry: Internal registry that manages field strategies for different data types.
    """

    def __init__(self) -> None:
        """Initialize the Service with an empty Registry."""
        self._registry = Registry()

    def register(self, strategy: Strategy) -> None:
        """Register a new field strategy.

        Args:
            strategy: Instance of :class:`Strategy` to register.

        Raises:
            StrategyNameAlreadyRegisteredError: If a strategy with the same type_name already exists.
            StrategyDtypeAlreadyRegisteredError: If a strategy with the same dtype already exists.
        """

        self._registry.register(strategy)

    def unregister(self, strategy: Strategy) -> None:
        """Unregister a previously registered strategy.

        Args:
            strategy: Instance of :class:`Strategy` to unregister.
        """
        self._registry.unregister(strategy.type_name)

    def update(self, strategy: Strategy) -> None:
        """Update an already registered strategy.

        If the strategy doesn't exist, it's registered as new.

        Args:
            strategy: Instance of :class:`Strategy` to update.
        """
        self._registry.update(strategy)

    # ------------------------------------------------------------------ #
    # Internal helpers                                                   #
    # ------------------------------------------------------------------ #
    def _field_payload(self, series: Series) -> dict:
        """Generate the schema for a specific column.

        If the series dtype is not associated with any strategy,
        a fallback strategy under the ``type_name`` "text" is attempted.

        Args:
            series: Pandas series to inspect.

        Returns:
            Dictionary with the column schema.

        Raises:
            FallbackStrategyMissingError: If no fallback strategy exists.
        """
        dtype = normalize_dtype(series.dtype)
        strat = self._registry.strategy_for_dtype(
            dtype
        ) or self._registry.strategy_for_name("text")
        if strat is None:
            raise FallbackStrategyMissingError(dtype)
        return strat.build_dict(series)

    # ------------------------------------------------------------------ #
    # Public API                                                         #
    # ------------------------------------------------------------------ #
    def _schema_payload(self, df: DataFrame) -> list[dict]:
        """Build the list of schemas for each column.

        Args:
            df: Source DataFrame.

        Returns:
            Ordered list of schemas.

        Raises:
            EmptyDataFrameError: If the DataFrame has no columns or is empty.
        """
        if df.columns.empty or df.empty:
            raise EmptyDataFrameError(df)
        return [self._field_payload(col) for _, col in df.items()]

    def build_schema(self, df: DataFrame) -> dict[str, list[dict]]:
        """Return the final payload ready for injection into the front-end.

        Args:
            df: Source DataFrame.

        Returns:
            JSON payload with the schema of each column.
        """
        return {"inputs": self._schema_payload(df), "outputs": []}
