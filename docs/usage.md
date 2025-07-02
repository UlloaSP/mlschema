# Usage

This section presents a concise, end‑to‑end guide for adopting **mlschema** in production environments. The library is intentionally segmented into two logical namespaces—`core` and `strategies`—to uphold the single‑responsibility principle while giving architects full control over extension points.

---

## 1. Core Module

Import the core abstractions to orchestrate schema generation:

```python
from mlschema.core import MLSchema, BaseField, FieldStrategy
```

| Class               | Responsibility                                                                                                                   |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| **`MLSchema`**      | Central coordinator. Maintains the registry of field strategies and owns the `build()` pipeline.                                 |
| **`BaseField`**     | Pydantic base model with the common contract. Extend it when you introduce new field types.                                      |
| **`FieldStrategy`** | Abstract base class for all strategies. Implement this to map DataFrame dtypes to concrete form controls.                        |

Instantiate the orchestrator:

```python
ms = MLSchema()
```

---

## 2. Strategies Module

`mlschema.strategies` ships with a curated set of ready‑made strategies that cover 90 % of mainstream use cases:

```python
from mlschema.strategies import (
    TextStrategy,
    NumberStrategy,
    CategoryStrategy,
    BooleanStrategy,
    DateStrategy,
)
```

| Strategy               | Custom Type                         | Supported dtypes (pandas)              |
| ---------------------- | ----------------------------------- | -------------------------------------- |
| **`TextStrategy`**     | `text`                              | `object`, `string`                     |
| **`NumberStrategy`**   | `number`                            | `int64`, `float64`, `int32`, `float32` |
| **`CategoryStrategy`** | `category`                          | `category`                             |
| **`BooleanStrategy`**  | `boolean`                           | `bool`, `boolean`                      |
| **`DateStrategy`**     | `date`                              | `datetime64[ns]`, `datetime64`         |

> **Note**
> No strategy is auto‑enabled. You decide which ones to register, ensuring a deliberate, transparent schema.

---

## 3. Strategy Lifecycle Management

`MLSchema` exposes three symmetrical operations. All of them use the strategy’s `type_name` as the primary key—avoid duplicates.

```python
# Register new strategies
ms.register(TextStrategy())
ms.register([NumberStrategy(), BooleanStrategy()])

# Replace an existing implementation in‑place
ms.update(TextStrategy())

# Remove a registered strategy
ms.unregister(TextStrategy())
```

*Registration is idempotent.* Calling `register()` with an already‑registered `type_name` raises an error; use `update()` instead.

---

## 4. Building a Form Schema

After curating your registry, translate a `pandas.DataFrame` into a front‑end‑ready JSON specification:

```python
import pandas as pd

# Source data
df = pd.read_csv("data.csv")

# Generate JSON schema
form_schema = ms.build(df)
print(form_schema)  # → JSON ready for your UI layer
```

The `build()` method scans each column, delegates to the first compatible strategy, and returns a validated and well-formed JSON.

> **Data‑type integrity is mandatory.**
> Ensure your DataFrame columns carry accurate dtypes. Undeclared or unsupported dtypes fall back to `TextStrategy`. If you rely on that behaviour, remember to register `TextStrategy`.

---

## 5. Advanced: Creating a Custom Strategy

When domain‑specific requirements emerge, extend the contract by pairing a bespoke `BaseField` with a `FieldStrategy` implementation.

```python
from typing import Literal
from pandas import Series, api
from pydantic import model_validator
from mlschema.core import BaseField, FieldStrategy

# 1️⃣  Define the Pydantic schema
class CustomField(BaseField):
    type: Literal["custom"] = "custom"  # Required: must be a Literal string, cannot be None
    min: float | None = None
    max: float | None = None
    value: float | None = None

    @model_validator(mode="after")
    def _constraints(self) -> "CustomField":
        if self.min and self.max and self.min > self.max:
            raise ValueError("min must be ≤ max")
        if self.value is not None:
            if self.min is not None and self.value < self.min:
                raise ValueError("value below min")
            if self.max is not None and self.value > self.max:
                raise ValueError("value above max")
        return self

# 2️⃣  Map DataFrame dtypes to the field
class CustomStrategy(FieldStrategy):
    def __init__(self) -> None:
        super().__init__(
            type_name="custom",
            schema_cls=CustomField,
            dtypes=("int64", "float64", "int32", "float32"),
        )

    def attributes_from_series(self, series: Series) -> dict:
        # Note: No need to set the 'type', 'title' and 'required' attributes - it's automatically handled by the parent class
        # You can set a description to the field by the 'description' attribute which is optional and must be a string between 1 and 500 characters
        description = "Custom Strategy Description"
        min = series.min()
        max = series.max()
        value = series.mean()
        return {"description": description, "min": min, "max": max, "value": value}
```

Register the strategy as usual and it integrates seamlessly with the `build()` pipeline.

---

## 6. Best‑Practice Checklist

1. **Plan your registry**: Register only the strategies you intend to expose.
2. **Avoid silent overwrites**: Use `update()` instead of `register()` for hot‑swaps.
3. **Validate your DataFrame**: Confirm that column dtypes align with the strategies you expect.
4. **Leverage Pydantic**: Embed robust validators in your custom `BaseField` models to enforce domain rules at build time.
5. **Version intelligently**: Because `type` is the primary key, apply semantic versioning to avoid collisions between major changes.

---****

## 7. Next Steps

Refer to the [API Reference](reference.md) for exhaustive method signatures, extension hooks, and advanced configuration scenarios.
