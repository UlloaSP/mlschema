"""Strategies sub-package for **MLSchema**

This namespace aggregates the concrete `Strategy` implementations that map
pandas dtypes to **validated JSON field definitions**.  All classes inherit from
`mlschema.core.Strategy` and are **opt-in**, they become active only after an
explicit `MLSchema.register()` call.

Strategies Available:
    | Class               | Description                                        |
    |---------------------|----------------------------------------------------|
    | BooleanStrategy     | Strategy for handling boolean data types.          |
    | CategoryStrategy    | Strategy for handling categorical data types.      |
    | DateStrategy        | Strategy for handling date and datetime data types.|
    | NumberStrategy      | Strategy for handling numeric data types.          |
    | TextStrategy        | Strategy for handling text and string data types.  |

Design notes
------------

| Principle                 | Description                                                                                                                     |
|---------------------------|-------------------------------------------------------------------------------------------------------------------------------- |
| **Single-responsibility** | Each strategy handles *one* logical field type.                                                                                 |
| **Pluggable**             | New strategies register via `MLSchema.register()`, replace via `MLSchema.update()`, and deregister via `MLSchema.unregister()`. |
| **Declarative output**    | Strategies emit validated `BaseField` subclasses, ensuring schema integrity from ingestion to UI rendering.                     |
"""

from .app import (
    BooleanStrategy,
    CategoryStrategy,
    DateStrategy,
    NumberStrategy,
    TextStrategy,
)

__all__ = [
    "BooleanStrategy",
    "CategoryStrategy",
    "DateStrategy",
    "NumberStrategy",
    "TextStrategy",
]
