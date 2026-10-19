---
title: Quick start
description: Shape a DataFrame, infer its fields, refine them, and send the result to a frontend.
---

MLschema reads column dtypes, names and nullability. The quality of the schema follows the quality
of those dtypes, so the first step is a DataFrame whose types say what each column means.

## 1. Give each column a deliberate dtype

```python
import pandas as pd

df = pd.read_csv("applicants.csv")
df = df.astype({"role": "category"})
df["joined"] = pd.to_datetime(df["joined"])
```

For this page, the same data built inline:

```python
df = pd.DataFrame(
    {
        "name": ["Ada", "Linus", "Grace"],
        "score": [98.5, 86.0, 91.0],
        "role": pd.Categorical(["engineer", "engineer", "scientist"]),
        "active": [True, False, True],
        "joined": pd.to_datetime(["2024-01-15", "2023-06-01", None]),
    }
)
```

## 2. Infer the fields

```python
from mlschema import infer_schema

fields = infer_schema(df)
```

`fields` is a plain `list[dict]`, one entry per column, in column order:

```json
[
  { "label": "name", "required": true, "mappedTo": "name", "kind": "text" },
  { "label": "score", "required": true, "mappedTo": "score", "kind": "number", "step": 0.1 },
  {
    "label": "role",
    "required": true,
    "mappedTo": "role",
    "kind": "category",
    "options": ["engineer", "scientist"]
  },
  { "label": "active", "required": true, "mappedTo": "active", "kind": "boolean" },
  { "label": "joined", "required": false, "mappedTo": "joined", "kind": "date" }
]
```

What each key came from:

- `kind` comes from the dtype: `str` falls back to `text`, `float64` is a `number`, `category` keeps
  its declared categories as `options`, `bool` is a `boolean`, and `datetime64[us]` is a `date`.
- `label` and `mappedTo` both start as the column name. `label` is display copy you can change;
  `mappedTo` is the key the model expects. See [Mappings](/schema/mappings/).
- `required` is `true` when the column has no missing values. `joined` has one, so it is optional.
- Unset optional attributes are omitted rather than sent as `null`.

## 3. Refine what inference cannot know

Labels, bounds, units and defaults are product decisions. Patch them by column name:

```python
fields = infer_schema(
    df,
    overrides={
        "score": {"label": "Quality score", "min": 0, "max": 100, "unit": "points"},
        "joined": {"label": "Joined on", "required": True},
    },
)
```

Overrides are validated with the rest of the field, so `"min": 200, "max": 100` fails instead of
reaching the interface. [Overrides](/guides/overrides/) covers the rules.

## 4. Send it to a frontend

The result is JSON-serialisable as returned:

```python
import json

payload = json.dumps(fields)
```

[MLForm](https://docs.mlform.eshkra.dev/) renders these fields as an accessible form and submits
values under each `mappedTo`. [Use with MLForm](/guides/mlform/) shows the handoff. Any other
consumer can branch on `kind`, as described in [Field contract](/schema/overview/).

## Next steps

- [Field kinds](/schema/field-kinds/): every built-in kind and how it is detected.
- [Mappings](/schema/mappings/): one-hot groups and models that take a positional feature vector.
- [Builders and custom kinds](/guides/extensions/): your own inference rules.
