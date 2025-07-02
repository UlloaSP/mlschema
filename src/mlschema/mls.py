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
    """Clase principal que encapsula el servicio de campos y su registro.

    Proporciona una interfaz para registrar, actualizar y desregistrar
    estrategias de campo, así como para acceder al servicio de campos.
    """

    def __init__(self) -> None:
        """Inicializa el servicio de campos."""
        self.field_service = FieldService()

    def register(self, strategy: FieldStrategy | list[FieldStrategy]) -> None:
        """Registra una nueva estrategia de campo.

        Parameters
        ----------
        strategy:
            Instancia de :class:`FieldStrategy` a registrar.
        """
        if isinstance(strategy, list):
            self.field_service.register_all(strategy)
        else:
            self.field_service.register(strategy)

    def unregister(self, strategy: FieldStrategy) -> None:
        """Desregistra una estrategia previamente registrada.

        Parameters
        ----------
        strategy:
            Instancia de :class:`FieldStrategy` a desregistrar.
        """
        self.field_service.unregister(strategy)

    def update(self, strategy: FieldStrategy) -> None:
        """Actualiza una estrategia ya registrada.

        Si la estrategia no existe, se registra como nueva.

        Parameters
        ----------
        strategy:
            Instancia de :class:`FieldStrategy` a actualizar.
        """
        self.field_service.update(strategy)

    def build(self, df: DataFrame) -> str:
        """Devuelve el *payload* final listo para inyección en el front-end.

        Parameters
        ----------
        df:
            DataFrame de pandas con las columnas a procesar.

        Returns
        -------
        str
            JSON serializado del esquema generado.
        """
        return self.field_service.build(df)
