from typing import Any

from pandas import DataFrame

from mlschema.core.app import Service, Strategy


class MLSchema:
    """Facade that orchestrates strategy registration and schema generation.

    The class wraps an internal :class:`mlschema.core.app.Service` instance and
    surfaces a minimal, stable API for client code.  It is therefore the
    canonical entry point when integrating **mlschema** into an application or
    pipeline.

    Attributes:
        field_service: Internal service component that performs the heavy lifting (registry management and JSON payload generation).
    """

    def __init__(self) -> None:
        self.field_service = Service()

    def register(self, strategy: Strategy) -> None:
        """Register a **new** strategy.

        Args:
            strategy: Instance of a concrete :class:`mlschema.core.app.Strategy`.

        Raises:
            StrategyNameAlreadyRegisteredError: If a strategy with the same name is already registered.
            StrategyDtypeAlreadyRegisteredError: If a strategy with the same dtype is already registered.
        """
        self.field_service.register(strategy)

    def unregister(self, strategy: Strategy) -> None:
        """Remove a **previously registered** strategy.

        Args:
            strategy: Strategy instance to be removed from the registry.
        """
        self.field_service.unregister(strategy)

    def update(self, strategy: Strategy) -> None:
        """Replace an existing strategy **in-place**.

        If either the ``type_name`` or any of the advertised ``dtypes``
        already exist, they are overwritten with the supplied strategy.

        Args:
            strategy: Instance of `Strategy` to update.
        """
        self.field_service.update(strategy)

    def build(self, df: DataFrame) -> dict[str, list[dict[str, Any]]]:
        """Translate a DataFrame into a JSON-serialisable form schema

        Args:
            df: Source data whose columns will be analysed and mapped to field definitions.

        Returns:
            Dictionary with the schema information, where keys are field names

        Raises:
            EmptyDataFrameError: If the DataFrame is empty.
            FallbackStrategyMissingError: If no fallback strategy is available for the DataFrame.
            PydanticCustomError: If there are validation errors in the schema.
        """
        return self.field_service.build_schema(df)
