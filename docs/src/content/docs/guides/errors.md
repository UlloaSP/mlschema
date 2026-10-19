---
title: Errors
description: The exceptions infer_schema raises, what triggers each one, and how to catch them.
---

MLschema never returns a partial or unvalidated schema. A failure raises before anything is
returned.

## Library exceptions

The exception classes are exported from `mlschema.core`:

```python
from mlschema.core import EmptyDataFrameError, FieldBuilderError, MLSchemaError
```

| Exception | Raised when |
| --- | --- |
| `EmptyDataFrameError` | The DataFrame has no rows or no columns. |
| `FieldBuilderError` | A builder returned something other than a `dict` or `None`, a field has no `kind`, no builder claimed a column, `onehot_separator` is empty, or an override names a missing column. |
| `UnknownFieldKindError` | A builder or override emitted a `kind` with no registered model. |
| `FieldKindAlreadyRegisteredError` | Two kinds share a name, including a custom kind named like a built-in. |
| `FieldKindError` | `kind()` received a model that is not a `BaseField` subclass, has no `kind` field, or has a `None` kind default. |

They form one hierarchy, so you can catch as narrowly as you need:

```text
MLSchemaError (Exception)
└── InvalidValueError (also ValueError)
    ├── FieldServiceError
    │   └── EmptyDataFrameError
    └── FieldKindError
        ├── FieldBuilderError
        ├── FieldKindAlreadyRegisteredError
        └── UnknownFieldKindError
```

Every `InvalidValueError` exposes `param` (the logical input that failed), `value` (the offending
value), and `context` (a dict of diagnostics, or `None`):

```python
try:
    infer_schema(df, overrides={"agee": {"label": "Age"}})
except FieldBuilderError as error:
    print(error.param, error.value)  # overrides ['agee']
```

| Exception | `context` |
| --- | --- |
| `EmptyDataFrameError` | `{"rows": <int>, "cols": <int>}` |
| `FieldKindAlreadyRegisteredError`, `UnknownFieldKindError` | `{"offender": <kind name>}` |

## Validation errors

Field models raise `pydantic.ValidationError` unchanged. It is not an `MLSchemaError`. Common
causes:

- `min` greater than `max` on `number` or `date`, `minLength` greater than `maxLength` on `text`,
  `minPoints` greater than `maxPoints` on `series`;
- a `defaultValue` outside the declared bounds or options;
- an attribute the kind does not declare, often a typo in an override;
- a `label` that is empty or longer than 100 characters;
- category options that are not strings.

## A boundary for services

A web service that infers schemas from uploaded data can turn both families into a client error:

```python
from pydantic import ValidationError

from mlschema import infer_schema
from mlschema.core import MLSchemaError


def schema_for(df):
    try:
        return infer_schema(df)
    except (MLSchemaError, ValidationError) as error:
        raise ValueError(f"Cannot build a schema: {error}") from error
```
