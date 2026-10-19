---
title: Builders and custom kinds
description: Claim columns with your own builders, and register new field kinds with a Pydantic model.
---

Two extension points cover what overrides cannot:

- a **builder** decides how a column becomes a field of an existing kind;
- a **kind** adds a new field contract: a discriminator, a model that validates it, and a builder
  that emits it.

Both run inside `infer_schema()`; nothing is registered globally.

## Builders

A builder is a callable that receives the column and a `FieldContext`, and returns a field dict to
claim the column or `None` to pass it on.

```python
from pandas import Series

from mlschema import FieldContext, FieldDict, infer_schema


def money_builder(series: Series, ctx: FieldContext) -> FieldDict | None:
    if not ctx.name.endswith("_eur"):
        return None
    return {
        "kind": "number",
        "label": ctx.name.removesuffix("_eur").replace("_", " ").capitalize(),
        "required": ctx.required,
        "mappedTo": ctx.mappedTo,
        "min": 0,
        "step": 0.01,
        "unit": "EUR",
    }


fields = infer_schema(df, builders=[money_builder])
```

Builders passed with `builders=[...]` run before custom kinds and built-ins, in list order. The
first non-`None` result owns the column. The result is validated like any inferred field, and
[overrides](/guides/overrides/) still apply to it.

A builder must return a `dict` or `None`. Anything else, a dict without `kind`, or a column no
builder claims raises `FieldBuilderError`. A `kind` with no registered model raises
`UnknownFieldKindError`.

### `FieldContext`

| Attribute | Type | Meaning |
| --- | --- | --- |
| `name` | `str` | Column label: the column name, or `feature_<n>` for positional columns. |
| `dtype` | `str` | Normalised dtype name, such as `"float64"` or `"category"`. |
| `required` | `bool` | `True` when the column has no missing values. |
| `index` | `int` | Zero-based column position in the DataFrame. |
| `mappedTo` | `str` or `int` | The column's backend target. Copy it into the field. |
| `infer_field` | `Callable[[Series], FieldDict]` | Runs the active pipeline on another series, for builders that infer nested fields. |

Copy `ctx.mappedTo` rather than rebuilding it from the name, so positional DataFrames keep their
integer targets.

## Custom kinds

Define a model that inherits from `BaseField` and gives `kind` a literal default, then pair it with
a builder through `kind()`:

```python
from typing import Literal

from pandas import Series

from mlschema import BaseField, FieldContext, FieldDict, infer_schema, kind


class DurationField(BaseField):
    kind: Literal["duration"] = "duration"
    minSeconds: int
    maxSeconds: int


def duration_builder(series: Series, ctx: FieldContext) -> FieldDict | None:
    if not ctx.dtype.startswith("timedelta64"):
        return None
    return {
        "kind": "duration",
        "label": ctx.name,
        "required": ctx.required,
        "mappedTo": ctx.mappedTo,
        "minSeconds": int(series.min().total_seconds()),
        "maxSeconds": int(series.max().total_seconds()),
    }


fields = infer_schema(df, kinds=[kind(model=DurationField, infer=duration_builder)])
```

For a column of `pd.to_timedelta(["90s", "2min"])` named `wait`:

```json
{
  "label": "wait",
  "required": true,
  "mappedTo": "wait",
  "kind": "duration",
  "minSeconds": 90,
  "maxSeconds": 120
}
```

`kind()` reads the kind name from the model's `kind` default. It raises `FieldKindError` when the
model does not inherit from `BaseField`, has no `kind` field, or has a `None` default. Two kinds with
the same name, including a custom kind named like a built-in, raise
`FieldKindAlreadyRegisteredError`.

Custom models inherit `extra="forbid"` from `BaseField`, so the builder and any override can only
emit attributes the model declares. `mappedTo` is required by `BaseField`; omit it only if your
model redeclares it, as `onehot-category` does.

A consumer must know the new kind before it can render it. In
[MLForm](https://docs.mlform.eshkra.dev/extend/custom-fields/), register a field definition with
the same `kind` name.

## Choosing the right tool

| Need | Use |
| --- | --- |
| A label, bound, unit or default for one column | [Override](/guides/overrides/) |
| The same metadata rule across many columns or DataFrames | Builder |
| A dtype MLschema does not map, rendered as an existing kind | Builder |
| A control the existing kinds cannot express | Custom kind |

Keep custom kinds rare and small. A new kind exists because a consumer must render or validate it
differently, not because a column needs a nicer label.
