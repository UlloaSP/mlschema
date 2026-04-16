# Usage

This section delivers a concise, end-to-end blueprint for adopting **mlschema** in production. The library is deliberately divided into two namespaces, ``core`` and ``strategies``, upholding the single-responsibility principle and granting solution architects full autonomy over extension points.

---

## 1. Canonical Entry Point

The sanctioned, future-proof gateway is the ``mlform`` package.

```python
from mlschema import MLSchema
```

| Class               | Responsibility                                                                                                                   |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| **`MLSchema`**      | Central coordinator. Maintains the registry of field strategies and owns the `build()` pipeline.                                 |

Instantiate the orchestrator:

```python
mls = MLSchema()
```

## 2. Core Module

Import the core abstractions to orchestrate schema generation:

```python
from mlschema.core import BaseField, Strategy
```

| Class               | Responsibility                                                                                                                   |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| **`BaseField`**     | Pydantic base model with the common contract. Extend it when you introduce new field types.                                      |
| **`Strategy`**      | Abstract base class for all strategies. Implement this to map DataFrame dtypes to concrete form controls.                        |

---

## 3. Strategies Module

`mlschema.strategies` ships with a curated set of ready‑made strategies that cover **85%** of mainstream use cases:

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
> If you rely on treating unsuported types, remember to register ``TextStrategy`` as it is the default fallback.

---

## 4. Strategy Lifecycle Management

`MLSchema` exposes three symmetrical operations. All of them use the strategy’s `type_name` as the primary key—avoid duplicates.

```python
# Register new strategies
mls.register(TextStrategy())

# Replace an existing implementation in‑place
mls.update(TextStrategy())

# Remove a registered strategy
mls.unregister(TextStrategy())
```

*Registration is idempotent.* Calling `register()` with an already‑registered `type_name` raises an error; use `update()` instead.

---

## 5. Building a Form Schema

After curating your registry, translate a `pandas.DataFrame` into a front‑end‑ready JSON specification:

```python
import pandas as pd

# Source data
df = pd.read_csv("data.csv")

# Generate JSON schema
form_schema = mls.build(df)
```

The `build()` method scans each column, delegates to the first compatible strategy, and returns a validated and well-formed JSON.

> **Data‑type integrity is mandatory.**
> Ensure your DataFrame columns carry accurate dtypes. Undeclared or unsupported dtypes fall back to `TextStrategy`. If you rely on that behaviour, remember to register `TextStrategy`.

---

## 6. Advanced: Creating a Custom Strategy

When domain‑specific requirements emerge, extend the contract by pairing a bespoke `BaseField` with a `Strategy` implementation.

```python
from typing import Literal
from pandas import Series, api
from pydantic import model_validator
from mlschema.core import BaseField, Strategy

# 1️⃣  Define the Pydantic schema
class CustomField(BaseField):
    type: Literal["custom"] = "custom"  # Required: must be a Literal string, cannot be None
    min: float | None = None
    max: float | None = None
    value: float | None = None

# 2️⃣  Define the Strategy
class CustomStrategy(Strategy):
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

## 7. Best‑Practice Checklist

1. **Plan your registry**: Register only the strategies you intend to expose.
2. **Avoid silent overwrites**: Use `update()` instead of `register()` for hot‑swaps.
3. **Validate your DataFrame**: Confirm that column dtypes align with the strategies you expect.
4. **Leverage Pydantic**: Embed robust validators in your custom `BaseField` models to enforce domain rules at build time.
5. **Version intelligently**: Because `type` is the primary key, apply semantic versioning to avoid collisions between major changes.

---

## 8. Next Steps

Refer to the [API Reference](reference.md) for exhaustive method signatures, extension hooks, and advanced configuration scenarios.
