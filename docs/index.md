# MLSchema

> Lightweight SDK for turning **pandas** DataFrames into front-end-ready field schemas. Designed to integrate cleanly with [mlform](https://ulloasp.github.io/mlform/), but fully usable as a standalone schema inference layer.

---

## Overview

**MLSchema** converts tabular data into validated JSON-serialisable field definitions.

It is intended for projects where a `pandas.DataFrame` is already the source of truth, but the frontend still needs a stable contract to render inputs, validate values, or generate data-entry workflows. Instead of maintaining hand-written form schemas beside the data pipeline, MLSchema infers the first version of that contract directly from DataFrame columns and dtypes.

The default workflow is intentionally small: call `infer_schema(df)` and receive a list of fields ready to be consumed by a frontend layer.

```python
import pandas as pd

from mlschema import infer_schema

df = pd.DataFrame(
    {
        "name": ["Ada", "Linus"],
        "score": [98.5, 86.0],
        "active": [True, False],
    }
)

schema = infer_schema(df)
```

The result is a validated field list:

```json
[
  {
    "kind": "text",
    "label": "name",
    "required": true
  },
  {
    "kind": "number",
    "label": "score",
    "required": true,
    "step": 0.1
  },
  {
    "kind": "boolean",
    "label": "active",
    "required": true
  }
]
```

---

## Why MLSchema

In many analytics and machine-learning systems, the same data contract is repeated across notebooks, APIs, dashboards, review tools, and prediction forms. That repetition is fragile: a column changes, a dtype is corrected, a categorical value is added, and the UI contract can silently drift away from the data.

MLSchema keeps the schema close to the DataFrame while still producing a frontend-friendly representation. The inferred schema is not a loose description; it is validated through Pydantic models before being returned.

The library is useful when the goal is not to build a form manually, but to derive a reliable baseline from data and then apply only the domain-specific refinements that matter.

---

## What It Provides

| Capability                    | Detail                                                                                              |
| ----------------------------- | --------------------------------------------------------------------------------------------------- |
| **Automatic field inference** | Detects text, number, category, boolean, date, and pair-shaped series columns.                      |
| **Validated output**          | Field dictionaries are checked against strict Pydantic models before they are returned.             |
| **Frontend-ready contracts**  | Output is JSON-serialisable and designed to be consumed by UI libraries such as `mlform`.           |
| **Safe defaults**             | Builtin kinds are enabled by default; no registry setup is required for common DataFrame workflows. |
| **Controlled extension**      | Custom builders and custom kinds allow domain-specific behaviour without changing consumer code.    |
| **Column-level refinement**   | Overrides provide final labels, bounds, defaults, placeholders, units, and UI metadata.             |

---

## Installation

Install MLSchema with `uv`:

```bash
uv add mlschema
```

For other package managers and environment details, see the [Installation](installation.md) guide.

---

## Quick Start

```python
import pandas as pd

from mlschema import infer_schema

df = pd.read_csv("data.csv")

schema = infer_schema(df)
```

The generated schema can be passed to a frontend renderer, stored as a contract, inspected in tests, or post-processed before being sent to an API client.

MLSchema works best when DataFrame dtypes are intentional. Numeric columns should use numeric dtypes, categorical columns should use `category`, date columns should use pandas datetime dtypes, and boolean columns should use boolean dtypes. Ambiguous object columns fall back to `text`.

---

## Builtin Field Kinds

MLSchema ships with builtin inference for the standard field types used in most form-generation workflows.

| Kind       | Detection                                                    |
| ---------- | ------------------------------------------------------------ |
| `series`   | Non-null cells are 2-element tuples, lists, or dictionaries. |
| `boolean`  | `bool`, `boolean`                                            |
| `category` | `category`                                                   |
| `date`     | `datetime64[ns]`, `datetime64[us]`, `datetime64`             |
| `number`   | `int64`, `int32`, `float64`, `float32`                       |
| `text`     | Fallback for columns not claimed by an earlier kind.         |

The order matters. More specific detections run first, and `text` runs last as the safe fallback.

---

## Refining Inferred Schemas

Inference gives the structural baseline. Production interfaces usually need a more explicit product contract: clearer labels, minimum and maximum values, defaults, units, placeholders, descriptions, or UI hints.

Use `overrides` for those final column-specific refinements.

```python
schema = infer_schema(
    df,
    overrides={
        "score": {
            "label": "Quality score",
            "min": 0,
            "max": 100,
            "unit": "points",
        },
    },
)
```

Overrides are applied after inference and before final validation. Invalid constraints are rejected instead of being returned as a broken frontend contract.

---

## Extending Inference

Use a custom builder when an existing kind is correct, but a specific column needs domain-aware metadata.

```python
from pandas import Series

from mlschema import FieldContext, infer_schema

def money_builder(series: Series, ctx: FieldContext) -> dict | None:
    if ctx.name != "amount_eur":
        return None

    return {
        "kind": "number",
        "label": "Amount",
        "required": ctx.required,
        "step": 0.01,
        "unit": "EUR",
        "min": 0,
    }

schema = infer_schema(df, builders=[money_builder])
```

Use a custom kind when the frontend needs a new field contract with its own discriminator and validation model.

```python
from typing import Literal

from pandas import Series

from mlschema import BaseField, FieldContext, infer_schema, kind

class DurationField(BaseField):
    kind: Literal["duration"] = "duration"
    unit: Literal["seconds"] = "seconds"
    minSeconds: int
    maxSeconds: int

def duration_builder(series: Series, ctx: FieldContext) -> dict | None:
    if ctx.dtype not in {"timedelta64[ns]", "timedelta64[us]"}:
        return None

    return {
        "kind": "duration",
        "label": ctx.name,
        "required": ctx.required,
        "unit": "seconds",
        "minSeconds": int(series.min().total_seconds()),
        "maxSeconds": int(series.max().total_seconds()),
    }

schema = infer_schema(
    df,
    kinds=[
        kind(model=DurationField, infer=duration_builder),
    ],
)
```

The extension model stays narrow by design: builtin inference handles the common path, builders handle reusable domain rules, custom kinds define new frontend contracts, and overrides apply final column-level decisions.

---

## Designed For mlform

MLSchema pairs naturally with [mlform](https://ulloasp.github.io/mlform/). MLSchema infers and validates the field contract; mlform can consume that contract to render interactive forms.

This separation keeps the Python side focused on schema inference and the frontend side focused on rendering, interaction, and submission workflows.

MLSchema can also be used without mlform wherever a validated, JSON-serialisable field schema is useful.

---

## Documentation

| Page                            | Purpose                                                                            |
| ------------------------------- | ---------------------------------------------------------------------------------- |
| [Installation](installation.md) | Environment setup and package installation.                                        |
| [Usage Guide](usage.md)         | Practical schema inference, overrides, builders, custom kinds, and series columns. |
| [API Reference](reference.md)   | Public symbols, signatures, and lower-level details.                               |
| [Changelog](changelog.md)       | Version history and migration notes.                                               |

---

## Links

| Resource    | URL                                                                |
| ----------- | ------------------------------------------------------------------ |
| GitHub      | [github.com/UlloaSP/mlschema](https://github.com/UlloaSP/mlschema) |
| mlform      | [github.com/UlloaSP/mlform](https://github.com/UlloaSP/mlform)     |
| mlform docs | [ulloasp.github.io/mlform](https://ulloasp.github.io/mlform/)      |
