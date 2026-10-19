---
title: Mappings
description: How fields name the model inputs they feed, how one-hot columns become one field, and how to target positional feature vectors.
---

Every field separates what people read from what the model receives:

- `label` is display copy. Change it freely.
- `mappedTo` is the backend target: the feature name or position the model expects. A consumer sends
  the field's value under this target.

MLschema derives both from the DataFrame. There is no mapping argument to `infer_schema()`; the
column names you train with are the targets.

## Named columns

A DataFrame with named columns produces string targets equal to the column name:

```json
{ "label": "age", "required": true, "mappedTo": "age", "kind": "number", "step": 1.0 }
```

An override can change `label` without touching `mappedTo`, so the interface can say "Age in years"
while the model still receives `age`.

## Positional columns

When the columns are exactly `0, 1, 2…`, as with `pd.DataFrame(numpy_array)`, MLschema generates
labels and uses integer positions as targets:

```python
fields = infer_schema(pd.DataFrame([[1, 0.5], [2, 1.5]]))
```

```json
[
  { "label": "feature_0", "required": true, "mappedTo": 0, "kind": "number", "step": 1.0 },
  { "label": "feature_1", "required": true, "mappedTo": 1, "kind": "number", "step": 0.1 }
]
```

Overrides for positional columns use the string keys `"0"`, `"1"`, and so on.

## One-hot groups

A model trained on one-hot encoded categories expects one 0/1 column per value. MLschema folds those
columns back into one `onehot-category` field, so people choose a value instead of setting flags.

```python
df = pd.DataFrame({"color__red": [1, 0], "color__blue": [0, 1], "age": [3, 4]})
fields = infer_schema(df)
```

```json
[
  {
    "label": "color",
    "required": true,
    "kind": "onehot-category",
    "options": [
      { "label": "red", "value": "red", "mappedTo": "color__red" },
      { "label": "blue", "value": "blue", "mappedTo": "color__blue" }
    ]
  },
  { "label": "age", "required": true, "mappedTo": "age", "kind": "number", "step": 1.0 }
]
```

A column joins a group when:

- its name contains the separator, with a non-empty prefix before the first occurrence and a
  non-empty value after it;
- its non-null values are all `0` or `1` (`True` and `False` count as `1` and `0`);
- at least one other column has the same prefix and also qualifies.

The prefix becomes the field label and each value becomes an option. Each option carries the
original column name as its `mappedTo`; the group field has none. The field appears where the first
encoded column was.

The default separator is `"__"`. Pass `onehot_separator` when your encoder uses another one; an
empty separator raises `FieldBuilderError`:

```python
fields = infer_schema(df, onehot_separator="_is_")
```

Positional columns are never grouped, because a group needs column names to label its options.
Binary positional columns stay ordinary fields.

## Models that take a feature vector

Many models, including scikit-learn estimators fitted on arrays, receive inputs by position rather
than by name. Infer with names, which keep labels and one-hot groups meaningful, then convert the
targets with `with_positional_mappings`:

```python
from mlschema import infer_schema, with_positional_mappings

df = pd.DataFrame({"age": [42, 55], "color__red": [1, 0], "color__blue": [0, 1]})
fields = infer_schema(df)

positional = with_positional_mappings(fields, ["age", "color__red", "color__blue"])
```

```json
[
  { "label": "age", "required": true, "mappedTo": 0, "kind": "number", "step": 1.0 },
  {
    "label": "color",
    "required": true,
    "kind": "onehot-category",
    "options": [
      { "label": "red", "value": "red", "mappedTo": 1 },
      { "label": "blue", "value": "blue", "mappedTo": 2 }
    ]
  }
]
```

`feature_names` is the model's input order, for example `model.feature_names_in_` or the column
order you trained with. The function:

- returns a deep copy and never mutates `fields` or `feature_names`;
- replaces each field's top-level `mappedTo`, or for `onehot-category` fields each option's
  `mappedTo`, with its position in `feature_names` when it is a string;
- keeps integer targets that are already valid positions;
- leaves everything else unchanged: labels, series `columns`, one-hot grouping, and any other nested
  value a custom kind may carry, even if it is named `mappedTo`.

It raises `ValueError` when `feature_names` is a single string, contains an empty or non-string
name, or has duplicates; when a target is missing, not in `feature_names`, or an integer outside
its range; and when a one-hot field has no options. Every field other than `onehot-category` must
therefore have a top-level `mappedTo`, including fields of custom kinds. It converts mappings only; the fields themselves are not
validated again, so pass it the output of `infer_schema()`.
