---
title: Series
description: Columns whose cells hold pairs become one series field with two typed columns.
---

`series` describes repeated observations stored in one DataFrame column, such as timestamp and
value readings. Each cell is one row; the two positions in every cell become two typed `columns`.

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

fields = infer_schema(df)
```

```json
[
  {
    "label": "reading",
    "required": true,
    "mappedTo": "reading",
    "kind": "series",
    "columns": [
      { "label": "field1", "required": true, "kind": "date", "id": "field1" },
      { "label": "field2", "required": true, "kind": "number", "step": 0.1, "id": "field2" }
    ]
  }
]
```

The series keeps one `mappedTo`, the column it came from. Columns have no `mappedTo`; a consumer
sends the rows under the series target.

## Detection

A column is a series when it has at least one non-null cell and every non-null cell is:

- a tuple or list with exactly two items, or
- a dict with exactly two keys.

Anything else, including scalar strings, three-item tuples, or a mix of pairs and scalars, is left
to the next builder. Missing cells are allowed and make the series optional (`"required": false`).

## Columns

`columns` always holds two entries, in order, with ids `field1` and `field2`. The ids identify the
cell position; they never change.

| Cell shape | Column labels |
| --- | --- |
| Tuple or list `(x, y)` | `field1`, `field2` |
| Dict `{"timestamp": x, "value": y}` | The first two keys of the first cell, as strings: `timestamp`, `value`. |

Each column is inferred like a top-level column from the values at its position, so it gets a kind,
`required`, and the kind's attributes, for example `step` or `options`. Its `required` reflects the
values inside non-null cells.

Columns accept the scalar kinds `text`, `number`, `date`, `category`, and `boolean`, plus any
[custom kind](/guides/extensions/#custom-kinds) passed to the same call. `series` and
`onehot-category` cannot be columns. A custom kind becomes a valid column kind for the rest of the
Python process once any call has received it, so pass the same `kinds` to every call rather than
relying on calls being isolated.

### How column values are typed

Values are split out of the cells into plain pandas series, so the usual
[dtype rules](/schema/field-kinds/#dtypes-that-fall-back-to-text) apply:

- `pd.Timestamp` and `datetime.datetime` values become `date`.
- Python `int`, `float`, and `bool` values become `number` or `boolean`.
- A position that mixes Python object types is converted to numbers when at least one value parses
  as a number, so `"23.5"` alongside `7` gives `number`.
- Strings, including ISO dates such as `"2024-01-01"`, stay `text`. So do `datetime.date` values,
  which pandas converts to `datetime64[s]`.

Convert values to `pd.Timestamp` and numbers before inference, or set the columns with an override.

## Point limits and column overrides

`minPoints` and `maxPoints` bound the number of rows. Both are positive integers and `minPoints`
cannot exceed `maxPoints`.

```python
fields = infer_schema(
    df,
    overrides={
        "reading": {
            "label": "Sensor reading",
            "minPoints": 1,
            "maxPoints": 100,
            "columns": [
                {"id": "field1", "kind": "date", "label": "Day", "required": True},
                {
                    "id": "field2",
                    "kind": "number",
                    "label": "Temperature",
                    "unit": "°C",
                    "required": True,
                },
            ],
        }
    },
)
```

An override replaces `columns` as a whole, so list both. Each column is validated by the model of
its kind: a `number` column accepts `min`, `max`, `step`, and `unit`; a `category` column needs
`options`. A column must not carry `mappedTo`, its ids must be `field1` then `field2`, and the list
must have exactly two entries; anything else raises `pydantic.ValidationError`.

## With MLForm

The shape matches an [MLForm series](https://docs.mlform.eshkra.dev/schema/series/): each row is an
object keyed by column id, such as `{ "field1": "2024-01-01", "field2": 23.5 }`, and the rows are
submitted under the series `mappedTo`. MLForm columns accept only its built-in scalar kinds, so a
series with a custom column kind needs a consumer that knows that kind. Aggregations and other
renderer options belong to the consumer; add them on the frontend.
