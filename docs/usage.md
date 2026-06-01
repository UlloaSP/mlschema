# Usage

`mlschema` converts a `pandas.DataFrame` into a frontend-ready field schema.

The library is designed for the point where tabular data becomes an input contract: model dashboards, prediction forms, review screens, annotation workflows, internal tools, and any UI that needs to render fields from data without hardcoding every control by hand.

The public API is intentionally small. In normal usage, `infer_schema()` is the only entry point required. Builtin field kinds are enabled by default, while custom builders and custom kinds provide controlled extension points when the default inference is not enough.

## Infer Fields

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

`infer_schema()` returns a JSON-serialisable list of field dictionaries.

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

A field is considered required when its source column contains no missing values. The column name becomes the default label, and each builtin kind contributes only the metadata that can be inferred safely from the data.

A DataFrame with no rows or no columns is rejected with `EmptyDataFrameError`.

## Builtin Kinds

Builtin inference covers the standard field types expected in most tabular form workflows.

| Kind       | Detection                                                    | Output behaviour                                                       |
| ---------- | ------------------------------------------------------------ | ---------------------------------------------------------------------- |
| `series`   | Non-null cells are 2-element tuples, lists, or dictionaries. | Infers two nested subfields recursively.                               |
| `boolean`  | `bool`, `boolean`                                            | Emits a boolean field contract.                                        |
| `category` | `category`                                                   | Emits `options` from categorical categories.                           |
| `date`     | `datetime64[ns]`, `datetime64[us]`, `datetime64`             | Emits a date field contract.                                           |
| `number`   | `int64`, `int32`, `float64`, `float32`                       | Emits `step: 1` for integer columns and `step: 0.1` for float columns. |
| `text`     | fallback                                                     | Claims any column not handled by an earlier kind.                      |

The builtin order is deliberate:

```text
series
boolean
category
date
number
text
```

`series` runs before `text` because it detects compound object cells by content. `text` runs last because it is the safe fallback for unsupported or ambiguous object columns.

This means ordinary usage does not require manual registration. A well-typed DataFrame is enough.

## Overrides

Inference should provide a correct structural baseline, but production forms usually need better labels, bounds, defaults, units, placeholders, or UI hints.

Use `overrides` for final field patches by column name.

```python
schema = infer_schema(
    df,
    overrides={
        "score": {
            "label": "Score",
            "description": "Normalised score used by the review workflow.",
            "min": 0,
            "max": 100,
            "unit": "points",
        },
    },
)
```

Overrides are applied after a field has been inferred and before the final Pydantic validation step. They are intentionally shallow: each override replaces or adds top-level attributes on the inferred field.

Missing override targets are rejected with `FieldBuilderError`. Invalid field constraints are rejected by Pydantic validation.

This makes overrides suitable for column-specific product decisions, not for hiding inference problems. If a column has the wrong dtype, fix the DataFrame before calling `infer_schema()`.

## Custom Builder For An Existing Kind

Use a custom builder when the field kind already exists but a domain-specific column needs different metadata.

For example, an amount column can still be a `number`, but with currency semantics and a finer step.

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

schema = infer_schema(
    df,
    builders=[money_builder],
)
```

Builders are evaluated before builtin inference. The first builder returning a field dictionary owns the column.

The effective resolution order is:

```text
user builders
custom kind builders
builtin builders
```

Returning `None` means “this builder does not claim the column”. Returning a dictionary means “this builder owns the column”.

A builder must return either `None` or a field dictionary with a registered `kind`. Invalid builder payloads raise `FieldBuilderError`, and unknown kinds raise `UnknownFieldKindError`.

## Custom Kind

Use a custom kind when the frontend contract needs a new discriminator, not just different metadata for an existing kind.

A custom kind is defined by pairing a strict Pydantic field model with an inference builder.

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

`kind()` reads the kind name from the model's `kind` default. The model must inherit from `BaseField`, must declare a `kind` field, and the kind default cannot be `None`.

Duplicate kind names are rejected. A custom kind named `number`, for example, conflicts with the builtin `number` kind.

Custom non-series field models are also made available as valid subfields for `series`.

## Series Columns

`series` is intended for compact two-dimensional values stored in a single DataFrame column, such as timestamp-value pairs.

```python
import pandas as pd

from mlschema import infer_schema

df = pd.DataFrame(
    {
        "reading": [
            (pd.Timestamp("2024-01-01"), 23.5),
            (pd.Timestamp("2024-01-02"), 24.1),
        ]
    }
)

schema = infer_schema(df)
```

Output:

```json
[
  {
    "kind": "series",
    "label": "reading",
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

Supported cell shapes are 2-element tuples, 2-element lists, and 2-key dictionaries.

```python
(pd.Timestamp("2024-01-01"), 23.5)
[pd.Timestamp("2024-01-01"), 23.5]
{"timestamp": pd.Timestamp("2024-01-01"), "value": 23.5}
```

Tuple and list cells use `field1` and `field2` as subfield labels. Dictionary cells use the first two keys as subfield labels.

Subfields are inferred recursively. Before that recursive inference, object subseries are coerced when possible: Python dates and datetimes become datetime series, parseable date strings become datetime series, and numeric-looking strings become numeric series.

Nested series are rejected. A `series` field cannot contain another `series` field as a subfield.

Cardinality can be documented with overrides.

```python
schema = infer_schema(
    df,
    overrides={
        "reading": {
            "label": "Sensor reading",
            "minPoints": 1,
            "maxPoints": 100,
        },
    },
)
```

`minPoints` and `maxPoints` must be positive integers, and `minPoints` cannot be greater than `maxPoints`.

## End-To-End Example

The following example combines the normal production path: builtin inference, a custom builder for an existing kind, a custom field kind, and final overrides.

```python
from typing import Literal

import pandas as pd
from pandas import Series

from mlschema import BaseField, FieldContext, infer_schema, kind

class DurationField(BaseField):
    kind: Literal["duration"] = "duration"
    unit: Literal["seconds"] = "seconds"
    minSeconds: int
    maxSeconds: int

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

df = pd.DataFrame(
    {
        "name": ["Ada", "Linus"],
        "age": [42, 55],
        "amount_eur": [12.5, 30.0],
        "duration": pd.timedelta_range("1 day", periods=2, freq="D"),
        "tier": pd.Categorical(["pro", "free"], categories=["free", "pro"]),
        "active": [True, False],
        "created": pd.date_range("2024-01-01", periods=2),
        "reading": [
            (pd.Timestamp("2024-01-01"), 23.5),
            (pd.Timestamp("2024-01-02"), 24.1),
        ],
    }
)

schema = infer_schema(
    df,
    builders=[money_builder],
    kinds=[
        kind(model=DurationField, infer=duration_builder),
    ],
    overrides={
        "name": {
            "label": "Full name",
            "description": "Visible customer name.",
            "placeholder": "Ada Lovelace",
            "minLength": 1,
            "maxLength": 80,
            "defaultValue": "Ada",
            "ui": {"autocomplete": "name"},
        },
        "age": {
            "label": "Age",
            "description": "Customer age in years.",
            "min": 0,
            "max": 120,
            "step": 1,
            "defaultValue": 42,
            "unit": "years",
        },
        "tier": {
            "label": "Plan",
            "defaultValue": "pro",
        },
        "active": {
            "label": "Enabled",
            "trueLabel": "Yes",
            "falseLabel": "No",
            "defaultValue": True,
        },
        "created": {
            "label": "Created at",
            "min": "2024-01-01",
            "max": "2024-12-31",
            "step": 1,
        },
        "reading": {
            "label": "Sensor reading",
            "minPoints": 1,
            "maxPoints": 100,
        },
        "duration": {
            "label": "Processing time",
        },
    },
)
```

The custom `money_builder` owns only `amount_eur`. All other ordinary columns continue through builtin inference. The custom `duration` kind handles timedelta columns. Overrides then apply product-facing labels, defaults, bounds, and UI metadata.

This keeps the schema pipeline predictable: inference discovers structure, builders encode reusable domain rules, and overrides apply final column-specific decisions.

## Errors

The most common runtime errors come from invalid input data, invalid builder output, duplicate kinds, unknown kinds, missing override targets, or failed Pydantic validation.

| Error                             | Meaning                                                                                                              |
| --------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `EmptyDataFrameError`             | The input DataFrame has no rows or no columns.                                                                       |
| `FieldBuilderError`               | A builder returned an invalid payload, omitted `kind`, no builder matched, or an override targeted a missing column. |
| `UnknownFieldKindError`           | A builder emitted a kind with no registered field model.                                                             |
| `FieldKindAlreadyRegisteredError` | Two registered kinds use the same name.                                                                              |
| `FieldKindError`                  | `kind()` received an invalid field model.                                                                            |
| `pydantic.ValidationError`        | The final field payload violates its field model.                                                                    |

`mlschema` does not silently accept invalid schema contracts. The output is validated before it is returned, so downstream UI code can rely on the generated field list.

## Practical Guidance

Keep DataFrame dtypes deliberate. `category`, `boolean`, `datetime64`, numeric dtypes, and pair-shaped series columns all carry useful schema information. Ambiguous object columns fall back to `text`.

Use overrides for presentation and constraints tied to a specific column.

Use builders for reusable project rules.

Use custom kinds only when the frontend needs a genuinely new field contract.

Avoid documenting or depending on internal registry or strategy classes. The supported public workflow is `infer_schema()`, optional `builders`, optional `kinds`, and optional `overrides`.
