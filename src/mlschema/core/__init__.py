"""Core abstractions and error contracts for **MLSchema**.

This module defines the *extension surface* on which all custom behaviour
is built.  Integrators subclass the abstractions below to introduce new data
types or override default processing logic, and they trap the accompanying
exceptions to maintain deterministic error handling across the pipeline.
"""

from mlschema.core.app import Strategy
from mlschema.core.domain import BaseField
from mlschema.core.exceptions import (
    EmptyDataFrameError,
    FallbackStrategyMissingError,
    FieldRegistryError,
    FieldServiceError,
    InvalidValueError,
    MLSchemaError,
    StrategyDtypeAlreadyRegisteredError,
    StrategyNameAlreadyRegisteredError,
)

__all__ = [
    "BaseField",
    "EmptyDataFrameError",
    "FallbackStrategyMissingError",
    "FieldRegistryError",
    "FieldServiceError",
    "InvalidValueError",
    "MLSchemaError",
    "Strategy",
    "StrategyDtypeAlreadyRegisteredError",
    "StrategyNameAlreadyRegisteredError",
]
