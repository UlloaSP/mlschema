---
title: Field contract
description: The payload infer_schema returns, the attributes every field shares, and how fields are validated and serialised.
---

`infer_schema()` returns a list of field dictionaries. There is no envelope: no version header, no
model metadata, no reports. Field order follows DataFrame column order, except that the columns of
a [one-hot group](/schema/mappings/#one-hot-groups) collapse into one field at the position of the
first encoded column.

```json
[
  { "label": "age", "required": true, "mappedTo": "age", "kind": "number", "step": 1.0 },
  { "label": "notes", "required": false, "mappedTo": "notes", "kind": "text" }
]
```

Each field is discriminated by `kind`. A consumer branches on it to choose a control, then reads the
kind-specific attributes it supports. [Field kinds](/schema/field-kinds/) lists them.

## Shared attributes

Every built-in and custom kind inherits these from `BaseField`.

| Attribute | Type | Set by inference | Meaning |
| --- | --- | --- | --- |
| `kind` | `str` | always | Field discriminator. |
| `label` | `str`, 1–100 characters | always | Display label. Starts as the column name. |
| `required` | `bool` | always | `true` when the source column has no missing values. Defaults to `false`. |
| `mappedTo` | `str` (non-empty) or `int` (≥ 0) | always, except `onehot-category` | Backend target the model expects. See [Mappings](/schema/mappings/). |
| `description` | `str`, up to 500 characters | no | Help text. |
| `valuePath` | `str` or `list[str]` | no | Key path a consumer uses to read the value. |
| `defaultValue` | depends on kind | no | Initial value. Each kind narrows the type and checks it against its constraints. |

Field models reject attributes they do not declare. A misspelt override such as `"maxLenght"` fails
during inference instead of producing a key that every consumer silently ignores.

## Required means "never missing"

`required` describes the training data, not the business rule. A column with at least one missing
value produces `"required": false`; one without produces `"required": true`. When a column that had
gaps must still be filled in production, override it:

```python
fields = infer_schema(df, overrides={"joined": {"required": True}})
```

## Serialisation

Fields are serialised with Pydantic in JSON mode, so the list can go straight to `json.dumps`.

- Attributes that are not set are omitted, never emitted as `null`. A consumer treats a missing key
  as "not configured".
- Numeric constraints declared as floats serialise as floats: an inferred integer step is `1.0`, and
  an override of `"min": 0` on a `number` field comes back as `0.0`. JSON readers such as JavaScript
  treat `1.0` and `1` as the same number.
- Key order within a field is not part of the contract.

The same DataFrame with the same arguments always produces the same list. Builders run in a fixed
order and the first one that claims a column wins; see
[resolution order](/schema/field-kinds/#resolution-order).

## Validation

Nothing is returned until every field has passed its model.

| Stage | Rejects | Error |
| --- | --- | --- |
| Input | A DataFrame with no rows or no columns. | `EmptyDataFrameError` |
| Kind registration | Duplicate kind names, models that are not `BaseField` subclasses or lack a `kind` default. | `FieldKindAlreadyRegisteredError`, `FieldKindError` |
| Builders | Non-dict results, a missing `kind`, a column no builder claims, overrides for missing columns. | `FieldBuilderError` |
| Kind lookup | A `kind` with no registered model. | `UnknownFieldKindError` |
| Field models | Contradictory or invalid constraints, defaults outside them, unknown attributes. | `pydantic.ValidationError` |

[Errors](/guides/errors/) describes each one and how to catch them.

## Reading the contract outside Python

The payload is meant for TypeScript, JavaScript, or any language that reads JSON. A consumer should:

- keep field order;
- branch on `kind`, and treat a kind it does not know as unsupported rather than guessing;
- respect `required`, `defaultValue`, and the kind's constraints;
- send values under each field's `mappedTo`, never under its `label`.

## What the contract leaves out

MLschema describes model inputs. Prediction outputs, reports, explanations, layout, transport, and
authentication belong to the application or to a renderer such as
[MLForm](https://docs.mlform.eshkra.dev/). Add an envelope at your application boundary if you need
one.
