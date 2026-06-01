# MLSchema

[![PyPI - Version](https://img.shields.io/pypi/v/mlschema.svg)](https://pypi.org/project/mlschema/)
[![Python Versions](https://img.shields.io/pypi/pyversions/mlschema.svg)](https://pypi.org/project/mlschema/)
[![CI](https://github.com/UlloaSP/mlschema/actions/workflows/ci.yml/badge.svg)](https://github.com/UlloaSP/mlschema/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/UlloaSP/mlschema.svg)](https://github.com/UlloaSP/mlschema/blob/main/LICENSE)

> Turn pandas DataFrames into validated, front-end-ready field schemas.

`mlschema` is a lightweight Python SDK for deriving JSON-serialisable field contracts from tabular data. It is designed for model inputs, prediction forms, review tools, annotation workflows, dashboards, and any frontend that needs to render fields from a `pandas.DataFrame` without hand-writing the same schema twice.

It pairs naturally with [mlform](https://github.com/UlloaSP/mlform), but the generated schema is plain JSON-compatible data and can be consumed by any frontend or service layer.

## Why MLSchema

DataFrame columns already carry useful contract information: names, dtypes, categories, nullability, dates, numeric values, and structured pairs. MLSchema turns that information into a validated field list.

Instead of maintaining separate form definitions beside the data pipeline, use `infer_schema(df)` as the baseline and refine only what is genuinely product-specific: labels, bounds, defaults, units, placeholders, UI hints, or custom field kinds.

```python id="54fwnz"
import pandas as pd

from mlschema import infer_schema

df = pd.DataFrame(
    {
        "name": ["Ada", "Linus", "Grace"],
        "score": [98.5, 86.0, 91.0],
        "role": pd.Categorical(["engineer", "engineer", "scientist"]),
        "active": [True, False, True],
    }
)

schema = infer_schema(df)
```

```json id="mt9rru"
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
    "kind": "category",
    "label": "role",
    "required": true,
    "options": ["engineer", "scientist"]
  },
  {
    "kind": "boolean",
    "label": "active",
    "required": true
  }
]
```

## Key Features

* Function-first API: `infer_schema(df)`.
* Builtin inference for `text`, `number`, `category`, `boolean`, `date`, and two-axis `series` fields.
* Pydantic v2 validation before any schema is returned.
* JSON-serialisable field-list output for frontend and service integration.
* Field refinements through `overrides`.
* Domain-specific behaviour through custom builders.
* New frontend contracts through strict custom kinds.
* Typed public API with `py.typed`, Pyright, Ruff, pytest, and CI.

## Requirements

* Python `>=3.14,<3.15`
* pandas `>=3.0.3,<4.0.0`
* pydantic `>=2.13.4,<3.0.0`

## Installation

```bash id="ejpqxw"
uv add mlschema
```

Alternative package managers:

```bash id="gqitqn"
pip install mlschema
```

```bash id="2n70wl"
poetry add mlschema
```

Pin a version when reproducible environments matter:

```bash id="yrqcr7"
uv add "mlschema==0.2.0"
```

## Quick Start

```python id="f7024l"
import pandas as pd

from mlschema import infer_schema

df = pd.DataFrame(
    {
        "customer": ["Ada", "Linus", "Grace"],
        "age": [42, 55, 38],
        "tier": pd.Categorical(["pro", "free", "pro"], categories=["free", "pro"]),
        "created": pd.date_range("2024-01-01", periods=3),
    }
)

schema = infer_schema(df)
```

The result can be returned from an API, stored as a contract, passed to a form renderer, or used in tests to detect schema drift.

MLSchema works best when DataFrame dtypes are deliberate. Numeric columns should use numeric dtypes, categorical columns should use `category`, date columns should use pandas datetime dtypes, and boolean columns should use boolean dtypes. Ambiguous object columns fall back to `text`.

## Schema Output

The canonical output is a field list.

There is no top-level envelope by default. MLSchema returns the contract directly:

```json id="25et3y"
[
  {
    "kind": "text",
    "label": "customer",
    "required": true
  },
  {
    "kind": "number",
    "label": "age",
    "required": true,
    "step": 1
  },
  {
    "kind": "category",
    "label": "tier",
    "required": true,
    "options": ["free", "pro"]
  },
  {
    "kind": "date",
    "label": "created",
    "required": true
  }
]
```

Each field includes:

* `kind`: the frontend discriminator.
* `label`: the human-readable label, inferred from the column name unless overridden.
* `required`: `true` when the source column contains no missing values.
* kind-specific metadata, such as `step`, `options`, `field1`, `field2`, or validation bounds.

Optional values set to `None` are omitted from the output.

## Builtin Kinds

Builtin kinds are enabled by default and resolved in a fixed order.

| Kind       | Detection                                                    | Notes                                                                  |
| ---------- | ------------------------------------------------------------ | ---------------------------------------------------------------------- |
| `series`   | Non-null cells are 2-element tuples, lists, or dictionaries. | Infers `field1` and `field2` recursively.                              |
| `boolean`  | `bool`, `boolean`                                            | Emits a boolean field contract.                                        |
| `category` | `category`                                                   | Emits `options` from categorical categories.                           |
| `date`     | `datetime64[ns]`, `datetime64[us]`, `datetime64`             | Emits a date field contract.                                           |
| `number`   | `int64`, `int32`, `float64`, `float32`                       | Emits `step: 1` for integer columns and `step: 0.1` for float columns. |
| `text`     | fallback                                                     | Claims columns not handled by earlier kinds.                           |

The order matters. `series` runs before `text` because it detects pair-shaped object cells by content. `text` runs last as the safe fallback.

## Series Columns

A `series` field represents a two-axis value stored in a single DataFrame column, such as timestamp-value readings.

```python id="vjf8bq"
import pandas as pd

from mlschema import infer_schema

df = pd.DataFrame(
    {
        "readings": [
            (pd.Timestamp("2024-01-01"), 23.5),
            (pd.Timestamp("2024-01-02"), 24.1),
            (pd.Timestamp("2024-01-03"), 22.8),
        ],
    }
)

schema = infer_schema(df)
```

```json id="f1a308"
[
  {
    "kind": "series",
    "label": "readings",
    "required": true,
    "field1": {
      "kind": "date",
      "label": "field1",
      "required": true
    },
    "field2": {
      "kind": "number",
      "label": "field2",
      "required": true,
      "step": 0.1
    }
  }
]
```

Supported cell shapes are:

```python id="iv6b5b"
(timestamp, value)
[timestamp, value]
{"timestamp": timestamp, "value": value}
```

Nested series are rejected. Cardinality constraints such as `minPoints` and `maxPoints` can be added with `overrides`.

## Refining Fields With Overrides

Inference provides the structural baseline. Production interfaces often need clearer labels, ranges, defaults, units, placeholders, or UI metadata.

```python id="v9tboo"
schema = infer_schema(
    df,
    overrides={
        "age": {
            "label": "Age",
            "description": "Customer age in years.",
            "min": 0,
            "max": 120,
            "step": 1,
            "unit": "years",
        },
        "tier": {
            "label": "Plan",
            "defaultValue": "pro",
        },
    },
)
```

Overrides are applied after inference and before final validation. Missing columns and invalid constraints fail explicitly instead of producing a broken schema.

## Extending MLSchema

Use a custom builder when an existing kind is correct, but the column needs domain-aware metadata.

```python id="0r5mdy"
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

Use a custom kind when the frontend needs a new field discriminator and a dedicated validation model.

```python id="96x5rn"
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

Resolution is predictable:

```text id="kwtd5b"
user builders
custom kind builders
builtin builders
```

The first builder returning a field dictionary owns the column.

## Validation And Errors

MLSchema validates the generated contract before returning it.

Common errors include:

| Error                             | Meaning                                                                                                              |
| --------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `EmptyDataFrameError`             | The input DataFrame has no rows or no columns.                                                                       |
| `FieldBuilderError`               | A builder returned an invalid payload, omitted `kind`, no builder matched, or an override targeted a missing column. |
| `UnknownFieldKindError`           | A builder emitted a kind with no registered field model.                                                             |
| `FieldKindAlreadyRegisteredError` | Duplicate kind names were registered.                                                                                |
| `FieldKindError`                  | `kind()` received an invalid field model.                                                                            |
| `pydantic.ValidationError`        | The final field payload violates its Pydantic model.                                                                 |

Library exceptions are available from `mlschema.core.exceptions` and re-exported from `mlschema.core`.

## With mlform

MLSchema focuses on inference and validation. [mlform](https://github.com/UlloaSP/mlform) can consume the generated field list to render interactive forms.

The split is intentional: Python owns the data contract; the frontend owns rendering, interaction, and submission.

## Documentation

* Documentation: https://ulloasp.github.io/mlschema/
* Usage guide: https://ulloasp.github.io/mlschema/usage/
* Schema standard: https://ulloasp.github.io/mlschema/schema-standard/
* API reference: https://ulloasp.github.io/mlschema/reference/
* Changelog: https://ulloasp.github.io/mlschema/changelog/

## Tooling And Quality

* MIT-licensed package distributed as wheel and sdist.
* Built with Hatchling.
* Typed with `py.typed`.
* Tested with `pytest` and `pytest-cov`.
* Checked with `ruff` and `pyright`.
* CI provided by GitHub Actions.

## Contributing

Contributions are welcome.

Useful commands for local development:

```bash id="2fzokc"
uv sync
uv run pre-commit install
uv run pytest
```

Project links:

* Issues: https://github.com/UlloaSP/mlschema/issues
* Discussions: https://github.com/UlloaSP/mlschema/discussions
* Contributing guide: https://github.com/UlloaSP/mlschema/blob/main/CONTRIBUTING.md

## Security

Please report security concerns privately by emailing `pablo.ulloa.santin@udc.es`.

The disclosure process is documented in [SECURITY.md](https://github.com/UlloaSP/mlschema/blob/main/SECURITY.md).

## License

Released under the MIT License.

* License: https://github.com/UlloaSP/mlschema/blob/main/LICENSE
* Third-party notices: https://github.com/UlloaSP/mlschema/blob/main/THIRD_PARTY_LICENSES.md

---

Made by [Pablo Ulloa Santin](https://github.com/UlloaSP) and contributors.
