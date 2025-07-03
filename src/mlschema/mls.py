"""MLSchema - A Python library for generating ML field schemas from pandas DataFrames.

This module provides the main MLSchema class that serves as the primary interface
for registering field strategies and building schemas from pandas DataFrames.

Examples:
    Basic usage of MLSchema:

    ```python
    from mlschema import MLSchema
    from mlschema.core import FieldStrategy
    import pandas as pd

    # Create an MLSchema instance
    ml_schema = MLSchema()

    # Create a sample DataFrame
    df = pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 35],
        'salary': [50000.0, 60000.0, 70000.0]
    })

    # Register custom field strategies if needed
    # custom_strategy = CustomFieldStrategy()
    # ml_schema.register(custom_strategy)

    # Build the schema
    schema_json = ml_schema.build(df)
    print(schema_json)
    ```
"""

from pandas import DataFrame

from mlschema.core.app import FieldService, FieldStrategy


class MLSchema:
    """Main class that encapsulates the field service and its registration.

    Provides an interface for registering, updating and unregistering
    field strategies, as well as accessing the field service.
    """

    def __init__(self) -> None:
        """Initialize the field service."""
        self.field_service = FieldService()

    def register(self, strategy: FieldStrategy | list[FieldStrategy]) -> None:
        """Register a new field strategy.

        Parameters
        ----------
        strategy:
            Instance of :class:`FieldStrategy` to register.
        """
        if isinstance(strategy, list):
            self.field_service.register_all(strategy)
        else:
            self.field_service.register(strategy)

    def unregister(self, strategy: FieldStrategy) -> None:
        """Unregister a previously registered strategy.

        Parameters
        ----------
        strategy:
            Instance of :class:`FieldStrategy` to unregister.
        """
        self.field_service.unregister(strategy)

    def update(self, strategy: FieldStrategy) -> None:
        """Update an already registered strategy.

        If the strategy doesn't exist, it's registered as new.

        Parameters
        ----------
        strategy:
            Instance of :class:`FieldStrategy` to update.
        """
        self.field_service.update(strategy)

    def build(self, df: DataFrame) -> str:
        """Return the final payload ready for injection into the front-end.

        Parameters
        ----------
        df:
            Pandas DataFrame with the columns to process.

        Returns
        -------
        str
            JSON serialized schema generated.
        """
        return self.field_service.build(df)
