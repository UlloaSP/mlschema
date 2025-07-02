# 🚀 Usage

The `mlschema` library splits functionality between two modules: **core** and **strategies**. Below are the key components and how to wire them together.

## Core Module

Import the core classes to create and manage your schema generator:

```python
from mlschema.core import MLSchema, BaseField, FieldStrategy
```

* **MLSchema**: Main orchestrator. Instantiate with `ms = MLSchema()`.
* **BaseField**: A ready-to-extend Pydantic schema base; use it when defining custom fields.
* **FieldStrategy**: Abstract base class; extend this to implement custom field-handling strategies.

## Strategies Module

Out of the box, `mlschema` provides these built-in strategies:

```python
from mlschema.strategies import (
    TextStrategy,
    NumberStrategy,
    CategoryStrategy,
    BooleanStrategy,
    DateStrategy
)
```

These classes implement common field-to-form mappings (text inputs, numeric sliders, picklists, checkboxes, date pickers).

## Strategy Management

By default, **no strategies are registered**—you choose which to include:

```python
ms = MLSchema()

# Register strategies
ms.register(TextStrategy())
ms.register(NumberStrategy())
ms.register(CategoryStrategy())

# Update an existing strategy
ms.update(CustomStrategy())

# Unregister a strategy by its class or instance
ms.unregister(TextStrategy)
```

This API lets you mix built-in and custom strategies according to your needs.

## Building a Form Schema

Once you’ve registered the desired strategies, convert a `pandas.DataFrame` into a JSON schema for forms:

```python
import pandas as pd

# Prepare data
df = pd.read_csv('data.csv')

# Build JSON schema
form_schema = ms.build(df)
print(form_schema)
```

The `build` method iterates your registered strategies, applies each to matching DataFrame columns, and emits a JSON-ready structure (suitable for front-end form generators).

## Advanced: Custom Strategy Example

Extend `FieldStrategy` to tailor behavior for specific fields:

```python
from pandas import Series, api
from mlschema.core import FieldStrategy, BaseField
from typing import Literal
from pydantic import model_validator


class NumberField(BaseField):

    type: Literal["number"] = "number"
    min: float | None = None
    max: float | None = None
    step: float | None = 1
    placeholder: str | None = None
    value: float | None = None
    unit: str | None = None

    @model_validator(mode="after")
    def _check_numeric_constraints(self) -> "NumberField":
        # Valida que *min* ≤ *value* ≤ *max*.
        if self.min is not None and self.max is not None and self.min > self.max:
            raise ValueError(f"min ({self.min}) debe ser ≤ max ({self.max})")

        if self.value is not None:
            if self.min is not None and self.value < self.min:
                raise ValueError(f"value ({self.value}) debe ser ≥ min ({self.min})")
            if self.max is not None and self.value > self.max:
                raise ValueError(f"value ({self.value}) debe ser ≤ max ({self.max})")
        return self


class NumberStrategy(FieldStrategy):
    def __init__(self) -> None:
        super().__init__(
            type_name="number";
            schema_cls=NumberField,
            dtypes=("int64", "float64", "int32", "float32"),
        )

    def attributes_from_series(self, series: Series) -> dict:
        # Paso por defecto: 0.1 para floats, 1 para enteros
        step = 0.1 if api.types.is_float_dtype(series.dtype) else 1
        return {"step": step}
```

For full details on APIs, method signatures, and advanced configuration, see the [API Reference](reference.md).
