# Schema Standard

> The MLSchema standard defines the JSON field contract emitted by `infer_schema()`: a validated, frontend-ready representation of tabular inputs derived from `pandas.DataFrame` columns.

---

## Overview

MLSchema is not a generic JSON Schema generator. It defines a compact field standard for data-driven interfaces: prediction forms, review tools, annotation workflows, internal dashboards, and frontend libraries such as [mlform](https://ulloasp.github.io/mlform/).

The standard is intentionally close to the DataFrame. Column names become labels, pandas dtypes drive field kinds, nullability determines whether a field is required, and Pydantic models validate the final contract before it is returned.

The canonical public workflow is:

```python
from mlschema import infer_schema

schema = infer_schema(df)
```

The result is always a list of field dictionaries.

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
  }
]
```

This page documents the schema contract itself: its payload shape, reserved attributes, builtin kinds, validation rules, extension model, and compatibility expectations.

---

## Design Principles

MLSchema follows a small set of constraints to keep generated schemas predictable across Python backends and frontend consumers.

The top-level payload is always a field list. There is no envelope, model metadata block, version header, or output schema section in the emitted payload. Those concerns can be added by downstream applications, but the MLSchema contract remains focused on input fields.

Each field is discriminated by `kind`. Consumers should branch on this value to decide how to render, validate, or transform the field.

Every emitted field is validated before it is returned. Invalid constraints are not passed through as “best effort” JSON.

The output is JSON-serialisable. Pydantic serialisation is performed in JSON mode and `None` values are omitted, which keeps the payload compact while preserving explicit defaults and constraints.

Builtin inference is enabled by default. Common DataFrame workflows do not require manual registration.

Extension is explicit. Domain behaviour enters through custom builders, custom kinds, and overrides; not by mutating internal registries or relying on private classes.

---

## Canonical Payload Shape

The MLSchema payload is a list of fields.

```json
[
  {
    "kind": "text",
    "label": "customer_name",
    "required": true,
    "minLength": 1,
    "maxLength": 100,
    "placeholder": "Enter full name"
  },
  {
    "kind": "number",
    "label": "satisfaction_score",
    "required": true,
    "min": 0,
    "max": 100,
    "step": 1,
    "unit": "points"
  }
]
```

Each object in the list represents one frontend field. Field order follows DataFrame column order.

A field dictionary contains three layers of information:

| Layer                    | Purpose                                                                   |
| ------------------------ | ------------------------------------------------------------------------- |
| Base attributes          | Shared contract present across field kinds.                               |
| Kind-specific attributes | Constraints and metadata belonging to a specific field kind.              |
| UI metadata              | Optional consumer-facing hints that do not change the core data contract. |

The standard does not require consumers to understand every key. A renderer can safely use `kind`, `label`, and `required` as the minimum baseline, then progressively support kind-specific attributes.

---

## Base Field Contract

All fields inherit from `BaseField`.

The required base attributes are:

| Attribute  | Type   | Meaning                                                   |
| ---------- | ------ | --------------------------------------------------------- |
| `kind`     | `str`  | Field discriminator.                                      |
| `label`    | `str`  | Human-readable label. Defaults to the column name.        |
| `required` | `bool` | `true` when the source column contains no missing values. |

Optional base attributes are omitted when not set.

| Attribute                   | Type                                     | Meaning                                                            |
| --------------------------- | ---------------------------------------- | ------------------------------------------------------------------ |
| `description`               | `str`                                    | Help text or domain explanation.                                   |
| `disabled`                  | `bool`                                   | Field is present but disabled.                                     |
| `hidden`                    | `bool`                                   | Field is present but hidden.                                       |
| `readOnly`                  | `bool`                                   | Field is visible but not editable.                                 |
| `disabledWhen`              | any                                      | Declarative condition for disabling the field.                     |
| `hiddenWhen`                | any                                      | Declarative condition for hiding the field.                        |
| `readOnlyWhen`              | any                                      | Declarative condition for making the field read-only.              |
| `asyncValidationDebounceMs` | `int`                                    | Debounce interval for asynchronous validation.                     |
| `inactiveFieldPolicy`       | `"include"`, `"omit"`, `"reset-on-hide"` | Submission policy when a field becomes inactive.                   |
| `valuePath`                 | `str` or `list[str]`                     | Alternative path used by consumers when reading or writing values. |
| `defaultValue`              | any                                      | Initial field value.                                               |
| `ui`                        | `dict`                                   | Free-form UI metadata for frontend consumers.                      |

Field models reject unknown attributes. This is deliberate: the schema should fail at generation time rather than leak unsupported keys into the frontend contract.

---

## Builtin Kind Resolution

Builtin kinds are enabled by default and evaluated in a fixed order.

```text
series
boolean
category
date
number
text
```

The order is part of the contract. More specific detections run before broader fallbacks. `series` runs first because it detects pair-shaped object cells by content. `text` runs last because it accepts any column that was not claimed earlier.

| Kind       | Detection                                                    | Inferred metadata   |
| ---------- | ------------------------------------------------------------ | ------------------- |
| `series`   | Non-null cells are 2-element tuples, lists, or dictionaries. | `field1`, `field2`  |
| `boolean`  | `bool`, `boolean`                                            | Base field metadata |
| `category` | `category`                                                   | `options`           |
| `date`     | `datetime64[ns]`, `datetime64[us]`, `datetime64`             | Base field metadata |
| `number`   | `int64`, `int32`, `float64`, `float32`                       | `step`              |
| `text`     | Fallback                                                     | Base field metadata |

The contract assumes that DataFrame dtypes are meaningful. A numeric column stored as `object` is not treated as `number` unless a custom builder or preprocessing step handles it.

---

## Required Semantics

`required` is inferred from nullability.

A column with no missing values produces:

```json
{
  "kind": "text",
  "label": "name",
  "required": true
}
```

A column containing at least one missing value produces:

```json
{
  "kind": "text",
  "label": "name",
  "required": false
}
```

This rule is intentionally simple. MLSchema does not infer business-level optionality. If a nullable training column should still be required in a production form, set that decision with `overrides`.

---

## Text Field

`text` represents free-form textual input and is also the fallback kind for columns not claimed by a more specific builtin.

Minimal inferred field:

```json
{
  "kind": "text",
  "label": "customer_name",
  "required": true
}
```

Extended field:

```json
{
  "kind": "text",
  "label": "Email",
  "required": true,
  "description": "Primary contact email.",
  "minLength": 5,
  "maxLength": 254,
  "pattern": "^[^@]+@[^@]+\\.[^@]+$",
  "placeholder": "user@example.com",
  "defaultValue": "ada@example.com"
}
```

Supported kind-specific attributes:

| Attribute     | Type  | Meaning                  |
| ------------- | ----- | ------------------------ |
| `minLength`   | `int` | Minimum accepted length. |
| `maxLength`   | `int` | Maximum accepted length. |
| `pattern`     | `str` | Validation pattern.      |
| `placeholder` | `str` | Input placeholder.       |

Validation rejects inconsistent length bounds, and default values must satisfy declared text constraints.

---

## Number Field

`number` represents integer and floating-point numeric input.

Integer columns infer `step: 1`.

```json
{
  "kind": "number",
  "label": "age",
  "required": true,
  "step": 1
}
```

Float columns infer `step: 0.1`.

```json
{
  "kind": "number",
  "label": "score",
  "required": true,
  "step": 0.1
}
```

Extended field:

```json
{
  "kind": "number",
  "label": "Revenue",
  "required": true,
  "description": "Revenue reported for the selected period.",
  "min": 0,
  "max": 1000000,
  "step": 0.01,
  "unit": "EUR",
  "placeholder": "Enter amount",
  "defaultValue": 0
}
```

Supported kind-specific attributes:

| Attribute     | Type   | Meaning                             |
| ------------- | ------ | ----------------------------------- |
| `min`         | number | Minimum accepted value.             |
| `max`         | number | Maximum accepted value.             |
| `step`        | number | Increment used by numeric controls. |
| `placeholder` | `str`  | Input placeholder.                  |
| `unit`        | `str`  | Unit displayed by consumers.        |

Validation rejects `min > max`. Default values must be inside the declared range.

---

## Category Field

`category` represents a closed set of options.

It is inferred from pandas categorical columns.

```python
df["tier"] = pd.Categorical(
    ["pro", "free"],
    categories=["free", "pro"],
)
```

Generated field:

```json
{
  "kind": "category",
  "label": "tier",
  "required": true,
  "options": ["free", "pro"]
}
```

Extended field:

```json
{
  "kind": "category",
  "label": "Plan",
  "required": true,
  "options": ["free", "pro"],
  "defaultValue": "pro"
}
```

Supported kind-specific attributes:

| Attribute | Type   | Meaning                                          |
| --------- | ------ | ------------------------------------------------ |
| `options` | `list` | Accepted values. Must contain at least one item. |

`defaultValue` must be one of the declared options.

Category options are taken from the categorical dtype categories when available. A defensive fallback may use non-null unique values, but production schemas should prefer explicit pandas categorical dtypes because they preserve the intended option set and order.

---

## Boolean Field

`boolean` represents true/false input.

```json
{
  "kind": "boolean",
  "label": "active",
  "required": true
}
```

Extended field:

```json
{
  "kind": "boolean",
  "label": "Enabled",
  "required": true,
  "trueLabel": "Yes",
  "falseLabel": "No",
  "defaultValue": true
}
```

Supported kind-specific attributes:

| Attribute    | Type  | Meaning                    |
| ------------ | ----- | -------------------------- |
| `trueLabel`  | `str` | Label for the true state.  |
| `falseLabel` | `str` | Label for the false state. |

Boolean fields support `defaultValue` through the base contract.

---

## Date Field

`date` represents date-like input inferred from pandas datetime columns.

```json
{
  "kind": "date",
  "label": "created",
  "required": true
}
```

Extended field:

```json
{
  "kind": "date",
  "label": "Created at",
  "required": true,
  "min": "2024-01-01",
  "max": "2024-12-31",
  "step": 1,
  "defaultValue": "2024-01-01"
}
```

Supported kind-specific attributes:

| Attribute | Type             | Meaning                       |
| --------- | ---------------- | ----------------------------- |
| `min`     | `str`            | Minimum accepted date string. |
| `max`     | `str`            | Maximum accepted date string. |
| `step`    | positive integer | Step used by date controls.   |

Validation rejects `min > max`. Default values must be inside the declared range.

The standard expects date strings to be serialised in a frontend-compatible format. ISO-style date strings are the recommended representation for cross-language consumers.

---

## Series Field

`series` represents a two-axis value stored in a single DataFrame column. Typical examples are timestamp-value readings, coordinate pairs, or ordered measurement pairs.

A series column is detected by content rather than dtype. Non-null cells must all be 2-element tuples, 2-element lists, or 2-key dictionaries.

```python
df = pd.DataFrame(
    {
        "reading": [
            (pd.Timestamp("2024-01-01"), 23.5),
            (pd.Timestamp("2024-01-02"), 24.1),
        ]
    }
)
```

Generated field:

```json
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
```

Supported cell shapes:

| Shape | Example                        | Subfield labels                       |
| ----- | ------------------------------ | ------------------------------------- |
| Tuple | `(x, y)`                       | `field1`, `field2`                    |
| List  | `[x, y]`                       | `field1`, `field2`                    |
| Dict  | `{"timestamp": x, "value": y}` | Dictionary keys converted to strings. |

Extended field:

```json
{
  "kind": "series",
  "label": "Sensor reading",
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
  },
  "minPoints": 1,
  "maxPoints": 100
}
```

Supported kind-specific attributes:

| Attribute   | Type             | Meaning                            |
| ----------- | ---------------- | ---------------------------------- |
| `field1`    | field object     | First inferred subfield.           |
| `field2`    | field object     | Second inferred subfield.          |
| `minPoints` | positive integer | Minimum accepted number of points. |
| `maxPoints` | positive integer | Maximum accepted number of points. |

Before subfield inference, object subseries may be coerced where possible. Python dates and datetimes become datetime series, parseable date strings become datetime series, and numeric-looking strings become numeric series. Other object values remain object values and continue through normal inference.

Nested series are rejected. A `series` field cannot contain another `series` field as `field1` or `field2`.

Invalid pair shapes are not claimed as `series`. Empty series, null-only series, malformed tuples, malformed lists, malformed dictionaries, scalar strings, and ordinary object values continue through the remaining builders.

---

## Determinism And Serialisation

The same DataFrame and the same inference configuration should produce the same field list.

MLSchema preserves DataFrame column order, normalises dtype names before matching, applies builders in a fixed order, validates fields with their registered Pydantic model, and serialises with JSON-compatible output.

`None` values are omitted. This keeps generated schemas compact and avoids forcing frontend consumers to distinguish between “not configured” and explicit `null`.

A minimal field therefore remains minimal:

```json
{
  "kind": "text",
  "label": "name",
  "required": true
}
```

An enriched field only includes the attributes that are actually set:

```json
{
  "kind": "text",
  "label": "Full name",
  "required": true,
  "description": "Visible customer name.",
  "minLength": 1,
  "maxLength": 80,
  "placeholder": "Ada Lovelace",
  "defaultValue": "Ada",
  "ui": {
    "autocomplete": "name"
  }
}
```

---

## Validation Model

Validation happens before the schema is returned.

The relevant validation layers are:

| Layer                  | Responsibility                                                           |
| ---------------------- | ------------------------------------------------------------------------ |
| DataFrame validation   | Rejects empty DataFrames.                                                |
| Kind registration      | Rejects duplicate kind names and invalid custom kind models.             |
| Builder validation     | Rejects invalid builder return values, missing kinds, and unknown kinds. |
| Field model validation | Enforces Pydantic constraints for each field kind.                       |
| Override validation    | Ensures patched fields still satisfy the target field model.             |

This makes the generated schema suitable for frontend consumers that expect a stable contract. Broken fields fail during generation instead of failing later in rendering or submission.

---

## Error Contract

MLSchema exposes library-level exceptions through `mlschema.core.exceptions` and re-exports them from `mlschema.core`.

| Error                             | Meaning                                                                                                           |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `MLSchemaError`                   | Base package exception.                                                                                           |
| `InvalidValueError`               | Base class for configuration or user input violations.                                                            |
| `FieldServiceError`               | Base runtime input inference error.                                                                               |
| `EmptyDataFrameError`             | The DataFrame has no rows or no columns.                                                                          |
| `FieldKindError`                  | `kind()` received an invalid model, a model without `kind`, or a `None` kind default.                             |
| `FieldBuilderError`               | A builder returned an invalid payload, omitted `kind`, no builder matched, or overrides targeted missing columns. |
| `FieldKindAlreadyRegisteredError` | Duplicate kind names were registered.                                                                             |
| `UnknownFieldKindError`           | A builder emitted a kind with no registered field model.                                                          |
| `pydantic.ValidationError`        | A field payload violated its Pydantic model constraints.                                                          |

Applications that only need a broad failure boundary can catch `MLSchemaError` for library-level failures and `pydantic.ValidationError` for contract validation failures.

---

## Compatibility Expectations

The MLSchema standard is intended to be consumed outside Python. Frontend consumers should treat the payload as a discriminated field list.

A consumer should:

* Preserve field order.
* Branch on `kind`.
* Treat unknown kinds as unsupported unless explicitly registered.
* Respect `required`, `defaultValue`, and kind-specific constraints.
* Ignore unknown `ui` metadata if it is not relevant to that renderer.
* Avoid relying on absent optional keys.
* Treat missing optional keys as “not configured”.

A consumer should not infer hidden semantics from labels or column order alone. The explicit field contract is the source of truth.

---

## Practical Schema Design

Good schemas start with deliberate DataFrames.

Use pandas numeric dtypes for numeric fields, categorical dtypes for closed option sets, boolean dtypes for boolean controls, and datetime dtypes for date controls. Object columns are acceptable, but they are ambiguous and usually fall back to `text`.

Use overrides for final product decisions: labels, descriptions, bounds, defaults, placeholders, units, boolean labels, point limits, and UI metadata.

Use custom builders for reusable rules that still map to existing kinds.

Use custom kinds when a new frontend contract is required.

Keep custom kinds small and explicit. A new kind should exist because a consumer needs to render or validate it differently, not because a column needs a nicer label.

Do not depend on internal registry, service, or strategy classes. The supported contract is built around `infer_schema()`, optional `builders`, optional `kinds`, and optional `overrides`.

---

## Boundary Of The Standard

MLSchema describes fields. It does not describe model weights, prediction responses, explanations, evaluation metrics, feature importance, transport protocols, authentication, storage, or UI layout.

Those concerns belong to the application layer.

This boundary is intentional. Keeping the standard limited to field contracts makes the payload stable, easy to validate, and simple to consume from Python, TypeScript, or any system that can read JSON.
