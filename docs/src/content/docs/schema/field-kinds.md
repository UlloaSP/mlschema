---
title: Field kinds
description: The seven built-in field kinds, the dtypes that select them, and the attributes each one accepts.
---

| Kind | Selected when | Inferred attributes |
| --- | --- | --- |
| [`series`](#series) | Every non-null cell is a two-element tuple or list, or a two-key dict. | `columns` |
| [`onehot-category`](#onehot-category) | Two or more named 0/1 columns share a prefix, such as `color__red`. | `options` |
| [`boolean`](#boolean) | dtype `bool` or `boolean` | none |
| [`category`](#category) | dtype `category` | `options` |
| [`date`](#date) | dtype `datetime64[ns]` or `datetime64[us]` | none |
| [`number`](#number) | dtype `int64`, `int32`, `float64`, or `float32` | `step` |
| [`text`](#text) | Any column no earlier builder claimed. | none |

Every kind also carries the [shared attributes](/schema/overview/#shared-attributes).

## Resolution order

For each column, MLschema asks builders in this order and keeps the first non-`None` result:

1. builders passed with `builders=[...]`;
2. builders of custom kinds passed with `kinds=[...]`;
3. the built-in builders, in the table order above.

One-hot groups are found before any builder runs, from column names and values, so a group is
never offered to a builder column by column.

`series` comes first among the built-ins because it reads cell contents, which every dtype rule
would otherwise ignore. `text` comes last because it accepts anything.

## Dtypes that fall back to text

Matching is by exact dtype name. Columns stored with other dtypes are valid, but they become
`text`:

- `object` columns, including numbers or booleans stored as Python objects;
- the string dtype pandas 3 uses by default for text;
- other integer and float widths, such as `int8`, `int16`, `uint8`, and `float16`;
- nullable extension dtypes `Int64` and `Float64` (`boolean` is supported);
- `datetime64[ms]`, `datetime64[s]`, and timezone-aware datetimes such as `datetime64[us, UTC]`;
- `timedelta64`.

Convert the column before inference, for example `df["count"] = df["count"].astype("int64")`, or
write a [builder](/guides/extensions/) that claims it.

## `text`

Free-form input, and the fallback kind.

| Attribute | Type | Rule |
| --- | --- | --- |
| `minLength` | `int` | Must not exceed `maxLength`. |
| `maxLength` | `int` | |
| `pattern` | `str` | A regular expression source, passed through unchanged. |
| `placeholder` | `str` | |
| `defaultValue` | `str` | Its length must respect `minLength` and `maxLength`. |

```json
{
  "label": "Email",
  "required": true,
  "mappedTo": "email",
  "kind": "text",
  "placeholder": "user@example.com",
  "minLength": 5,
  "maxLength": 254,
  "pattern": "^[^@]+@[^@]+\\.[^@]+$"
}
```

MLschema does not compile `pattern`. Browser consumers such as MLForm evaluate it as a JavaScript
regular expression, so keep to syntax both languages share.

## `number`

Integer and floating-point input. Inference sets `step` to `1.0` for integer columns and `0.1` for
float columns.

| Attribute | Type | Rule |
| --- | --- | --- |
| `min` | number | Must not exceed `max`. |
| `max` | number | |
| `step` | number | Defaults to `1` when a builder omits it. |
| `unit` | `str` | Shown next to the value. |
| `placeholder` | `str` | |
| `defaultValue` | number | Must lie within `min` and `max`. |

```json
{
  "label": "Revenue",
  "required": true,
  "mappedTo": "revenue",
  "kind": "number",
  "min": 0.0,
  "max": 1000000.0,
  "step": 0.01,
  "unit": "EUR"
}
```

## `category`

A closed set of string options. Inference takes `options` from the categorical dtype, so declared
order and unused categories are kept:

```python
df["tier"] = pd.Categorical(["pro", "free"], categories=["free", "pro", "team"])
```

```json
{
  "label": "tier",
  "required": true,
  "mappedTo": "tier",
  "kind": "category",
  "options": ["free", "pro", "team"]
}
```

| Attribute | Type | Rule |
| --- | --- | --- |
| `options` | `list[str]` | At least one option. |
| `defaultValue` | `str` | Must be one of `options`. |

Options must be strings. A categorical column whose categories are numbers fails validation; convert
the categories first, for example with `df["grade"].cat.rename_categories(str)`.

## `onehot-category`

One choice that the model receives as several 0/1 columns. The field has no `mappedTo` of its own;
each option names its column.

```json
{
  "label": "color",
  "required": true,
  "kind": "onehot-category",
  "options": [
    { "label": "red", "value": "red", "mappedTo": "color__red" },
    { "label": "blue", "value": "blue", "mappedTo": "color__blue" }
  ]
}
```

| Attribute | Type | Rule |
| --- | --- | --- |
| `options` | list of `{label, value, mappedTo}` | At least one option. `label` and `value` are non-empty strings. |
| `defaultValue` | `str` | An option `value`. |

Grouping rules and separators are described in [Mappings](/schema/mappings/#one-hot-groups).

## `boolean`

True or false.

| Attribute | Type |
| --- | --- |
| `trueLabel` | `str` |
| `falseLabel` | `str` |
| `defaultValue` | `bool` |

```json
{
  "label": "Enabled",
  "required": true,
  "mappedTo": "enabled",
  "defaultValue": true,
  "kind": "boolean",
  "trueLabel": "Yes",
  "falseLabel": "No"
}
```

## `date`

A calendar date. Inference sets no bounds; add them with overrides.

| Attribute | Type | Rule |
| --- | --- | --- |
| `min` | `str` | ISO date such as `"2024-01-01"`. Must not be later than `max`. |
| `max` | `str` | ISO date. |
| `step` | positive `int` | |
| `defaultValue` | `str` | ISO date within `min` and `max`. |

Bounds are compared as strings, which orders ISO `YYYY-MM-DD` dates correctly. Use that format.

```json
{
  "label": "Created at",
  "required": true,
  "mappedTo": "created",
  "defaultValue": "2024-01-01",
  "kind": "date",
  "min": "2024-01-01",
  "max": "2024-12-31"
}
```

## `series`

A table of repeated observations stored in one column, such as timestamp and value pairs. Each cell
becomes a row; the two positions in the cell become `columns`. [Series](/schema/series/) describes
detection, column inference, and point limits.
