---
title: Overrides
description: Patch inferred fields by column name with labels, bounds, defaults and units, validated like any other field.
---

Inference finds the structure. Overrides add what only you know: the label people read, the valid
range, the unit, the default.

```python
fields = infer_schema(
    df,
    overrides={
        "age": {
            "label": "Age",
            "description": "Age in completed years.",
            "min": 0,
            "max": 120,
            "unit": "years",
            "defaultValue": 42,
        },
        "tier": {"label": "Plan", "defaultValue": "pro"},
        "active": {"label": "Enabled", "trueLabel": "Yes", "falseLabel": "No"},
        "created": {"label": "Created at", "min": "2024-01-01", "max": "2024-12-31"},
    },
)
```

## How a patch is applied

1. A builder infers the field for the column.
2. The override's keys replace or add top-level keys of that field. Nested values, such as `options`
   or series `columns`, are replaced whole, not merged.
3. The patched field is validated by its kind's model.

Because validation runs last, an override cannot produce a broken contract. Contradictory bounds,
a default outside them, a category default that is not an option, or an attribute the kind does not
declare all raise `pydantic.ValidationError`.

## Keys are column names

Override keys are matched against `str(column)` for every DataFrame column. A key that matches no
column raises `FieldBuilderError` before any field is inferred, so typos fail loudly.

For a DataFrame with positional columns `0, 1, 2…`, the keys are the strings `"0"`, `"1"`, and so
on. The generated `feature_0` label is not a key.

The columns of a [one-hot group](/schema/mappings/#one-hot-groups) are combined before overrides
apply, so an override cannot reach the group field: its encoded column names exist but are not
used, and the group name is not a column. To change a group, post-process the returned list.

## Overrides are for decisions, not repairs

An override that changes `kind` keeps the other inferred keys, which the new kind may reject. For
example, overriding an integer column with `{"kind": "text"}` fails because `step` is not a text
attribute. Fix the dtype before inference, or write a [builder](/guides/extensions/) that emits the
field you want.

Use overrides for column-specific product choices. When the same rule applies to many columns or
many DataFrames, a builder is the better home.
