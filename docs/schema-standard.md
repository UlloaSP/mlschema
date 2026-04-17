# The MLSchema Standard: A Extensible Contract for Machine Learning

> This section explains the foundational design principles behind the MLSchema JSON format, how it achieves vendor-agnostic compatibility, and the deliberate constraints that enable safe extensibility.

---

## 1. Executive Overview

**MLSchema** is not merely a pandas → JSON converter. It establishes a **data contract** between machine learning models and consumer applications—ensuring that model inputs and outputs can be reliably described, validated, and rendered across heterogeneous systems.

Unlike ad-hoc form definitions or proprietary model serialization formats, MLSchema proposes a **standard** that is:

- **Reproducible**: The same DataFrame always produces identical schemas.
- **Validated**: Every field complies with domain-specific constraints (ranges, patterns, cardinality).
- **Extensible**: New field types can be registered without breaking existing consumers.
- **Transport-agnostic**: JSON serialization permits language-agnostic integration with web frameworks, microservices, and low-code platforms.

### Why a Standard Matters

When a machine learning team deploys a model, downstream consumers must understand:
- Which inputs the model accepts.
- What types and ranges each input expects.
- How to present those inputs in a UI (text box, slider, dropdown, date picker).
- What the output schema looks like.

Without a formal specification, teams waste cycles reverse-engineering model contracts or hand-rolling form definitions. A standard eliminates that friction and unlocks reproducible, governable inference pipelines.

## 2. Core Principles

### 2.1 Strategy-Driven Architecture

MLSchema adopts the **strategy pattern** as its foundational design principle. Each pandas dtype is mapped to exactly one field type via a pluggable strategy:

```text
pandas dtype (e.g., "int64")
    ↓
Strategy registry lookup
    ↓
Pydantic BaseField subclass
    ↓
JSON schema
```

**Why strategies?**

1. **Single Responsibility**: Each strategy owns one problem domain (text encoding, numeric validation, categorical enumerations).
2. **Hot-Swap Extensibility**: Register custom strategies without modifying core code.
3. **Forward Compatibility**: Introduce domain-specific controls (geospatial, IoT widgets) as standalone strategies.

### 2.2 Mandatory Field Attributes

Every field in an MLSchema schema carries reserved attributes defined by the `BaseField` Pydantic model and always present in generated output:

| Attribute   | Type         | Constraint               | Example              |
|-------------|--------------|--------------------------|----------------------|
| `label`     | `str`        | 1–100 characters         | `"Age"`              |
| `required`  | `bool`       | Derived from nullability | `true`               |
| `kind`      | `str`        | Strategy-specific        | `"text"`, `"number"` |

Optional attributes (omitted when `None`):

| Attribute                  | Type                                        | Description                                  |
|----------------------------|---------------------------------------------|----------------------------------------------|
| `description`              | `str \| None`                               | Help text (max 500 chars)                    |
| `disabled`                 | `bool \| None`                              | Field is disabled                            |
| `hidden`                   | `bool \| None`                              | Field is hidden                              |
| `readOnly`                 | `bool \| None`                              | Field is read-only                           |
| `disabledWhen`             | `Any \| None`                               | Declarative condition to disable the field   |
| `hiddenWhen`               | `Any \| None`                               | Declarative condition to hide the field      |
| `readOnlyWhen`             | `Any \| None`                               | Declarative condition to make read-only      |
| `asyncValidationDebounceMs`| `int \| None`                               | Debounce in ms for async validation          |
| `inactiveFieldPolicy`      | `"include" \| "omit" \| "reset-on-hide"`    | Behaviour when field becomes inactive        |
| `valuePath`                | `str \| list[str] \| None`                  | Key path for reading the value on submit     |
| `defaultValue`             | `Any \| None`                               | Initial value for the field                  |
| `ui`                       | `dict[str, Any] \| None`                    | Arbitrary UI-layer props                     |

These attributes are **reserved**. Custom strategies must not emit them via `attributes_from_series()`.

### 2.3 Domain-Specific Extensions

Each strategy introduces optional attributes that refine the field contract:

- **NumberField**: `defaultValue` (inherited from `BaseField`), `min`, `max`, `step`, `unit`, `placeholder`
- **TextField**: `defaultValue` (inherited from `BaseField`), `minLength`, `maxLength`, `pattern`, `placeholder`
- **CategoryField**: `defaultValue` (inherited from `BaseField`), `options`
- **BooleanField**: `defaultValue` (inherited from `BaseField`), `trueLabel`, `falseLabel`
- **DateField**: `defaultValue` (inherited from `BaseField`), `min`, `max`, `step`
- **SeriesField**: `field1`, `field2`, `minPoints`, `maxPoints`

These extensions are **not** free-form; they are rigorously typed and validated by Pydantic models.

### 2.4 Deterministic Output

The same DataFrame always produces identical JSON. This is guaranteed by:

1. Normalizing pandas dtypes (e.g., `np.int64` → `"int64"`).
2. Preserving column order and names.
3. Using Pydantic's `model_dump()` with consistent serialization settings (`mode="json"`, `exclude_none=True`).

Deterministic output is critical for CI/CD pipelines, caching, and contract versioning.

---

## 3. The MLSchema JSON Format

### 3.1 Canonical Structure

MLSchema generates JSON payloads with the following canonical shape:

```json
{
  "inputs": [
    {
      "label": "customer_name",
      "kind": "text",
      "required": true,
      "minLength": 1,
      "maxLength": 100,
      "placeholder": "Enter full name"
    },
    {
      "label": "satisfaction_score",
      "kind": "number",
      "required": true,
      "min": 0,
      "max": 100,
      "step": 1,
      "unit": "points"
    }
  ],
  "outputs": []
}
```

The top-level envelope (`inputs`, `outputs`) provides logical separation between model parameters and expected predictions.

### 3.2 Field Type Taxonomy

MLSchema ships with six built-in field types:

#### **Kind: `text`**

```json
{
  "kind": "text",
  "label": "email",
  "required": true,
  "minLength": 5,
  "maxLength": 254,
  "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
  "placeholder": "user@example.com"
}
```

**Supported pandas dtypes**: `object`, `string`

#### **Kind: `number`**

```json
{
  "kind": "number",
  "label": "revenue",
  "required": true,
  "min": 0,
  "max": 1000000,
  "step": 0.01,
  "unit": "USD",
  "placeholder": "Enter amount"
}
```

**Supported pandas dtypes**: `int64`, `float64`, `int32`, `float32`

#### **Kind: `category`**

The `options` key is mandatory and is automatically derived from the DataFrame's unique categorical values.

```json
{
  "kind": "category",
  "label": "customer_segment",
  "required": true,
  "options": ["Bronze", "Silver", "Gold"]
}
```

**Supported pandas dtypes**: `category`

#### **Kind: `boolean`**

```json
{
  "kind": "boolean",
  "label": "is_active",
  "required": true,
  "trueLabel": "Yes",
  "falseLabel": "No"
}
```

**Supported pandas dtypes**: `bool`, `boolean`

#### **Kind: `date`**

`min` and `max` are ISO date strings (`YYYY-MM-DD`). Backend validation ensures `min ≤ max` via lexicographic comparison (valid for ISO format).

```json
{
  "kind": "date",
  "label": "contract_renewal",
  "required": false,
  "min": "2024-01-01",
  "max": "2026-12-31",
  "step": 7
}
```

**Supported pandas dtypes**: `datetime64[ns]`, `datetime64`

#### **Kind: `series`**

Represents a two-axis column where each cell is a 2-element compound value. Sub-fields are inferred automatically from element dtypes; nesting series inside series is explicitly rejected.

```json
{
  "kind": "series",
  "label": "readings",
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
  "minPoints": 10,
  "maxPoints": 1000
}
```

**Detection**: Content-based (not dtype-based). `SeriesStrategy` claims any `object` column whose non-null cells are all 2-element tuples, lists, or dicts.

**Supported cell formats**:

| Format | Example | Sub-field labels |
| ------ | ------- | ---------------- |
| Tuple | `(v1, v2)` | `field1`, `field2` |
| List | `[v1, v2]` | `field1`, `field2` |
| Dict | `{"k1": v1, "k2": v2}` | dict keys |

**Constraints**:

| Constraint | Rule | Error |
| ---------- | ---- | ----- |
| `field1` / `field2` not series | No nesting | `PydanticCustomError("no_series_nesting")` |
| Sub-field kind known | Must be registered via `add_series_sub_field()` | `PydanticCustomError("unknown_sub_field_type")` |
| `minPoints` / `maxPoints` ≥ 1 | `PositiveInt` | Pydantic validation error |
| `minPoints ≤ maxPoints` | Model validator | `PydanticCustomError("series_points_constraint")` |

### 3.3 Report Type Taxonomy

MLSchema ships with two built-in report types for describing model outputs:

#### **Kind: `regressor`**

```json
{
  "kind": "regressor",
  "label": "Predicted price",
  "source": "model_output",
  "unit": "EUR",
  "precision": 2
}
```

| Attribute      | Type           | Description                                    |
|----------------|----------------|------------------------------------------------|
| `unit`         | `str \| None`  | Unit label (e.g. `"€"`, `"kg"`)               |
| `precision`    | `int \| None`  | Decimal places shown (mlform default: 2)       |
| `explanations` | `bool \| None` | Show feature-importance explanations           |

#### **Kind: `classifier`**

```json
{
  "kind": "classifier",
  "label": "Predicted class",
  "source": "model_output",
  "labels": ["cat", "dog", "bird"],
  "details": true
}
```

| Attribute      | Type             | Description                                    |
|----------------|------------------|------------------------------------------------|
| `labels`       | `list[str] \| None` | Ordered class labels                        |
| `details`      | `bool \| None`   | Show per-class breakdown (mlform default: true)|
| `explanations` | `bool \| None`   | Show feature-importance explanations           |

---

## 4. Design Decisions & Rationale

### 4.1 Why Pydantic?

Pydantic v2 provides:

1. **Type safety**: Schemas are validated at construction time, not at serialization.
2. **Composability**: Custom models inherit from `BaseField`, enabling incremental extension.
3. **Standard format**: Pydantic models emit JSON in a deterministic, language-agnostic format.
4. **Validators**: Embedded, reusable validation logic (e.g., `min ≤ max`, regex patterns).

### 4.2 Why a Literal Type Annotation?

The `kind` field in each Pydantic model uses Python's `Literal` type:

```python
class NumberField(BaseField):
    kind: Literal[FieldTypes.NUMBER] = FieldTypes.NUMBER
```

This ensures:

- **Type narrowing**: IDEs and static analyzers can discriminate on the `kind` field.
- **Exhaustiveness**: Consumer code can enforce complete handling of all field types.
- **No collisions**: Only one schema matches a given `kind` string.

### 4.3 Why Reserved Keys?

The reserved keys (`label`, `kind`, `required`, `description`) are **always** populated by the base `Strategy` class. Custom strategies cannot override them via `attributes_from_series()`. This ensures:

1. **Predictability**: Consumers know these keys will always be present and meaningful.
2. **Schema integrity**: The contract is never violated by careless implementations.
3. **Versioning safety**: Future MLSchema versions can extend reserved keys safely.

### 4.4 Why `exclude_none=True`?

Pydantic's serialization mode `exclude_none=True` strips `null` values:

```json
{
  "kind": "text",
  "label": "email",
  "required": true,
  "minLength": 1
  // "placeholder": null is excluded
}
```

Optional attributes are **omitted** when not set, keeping payloads compact.

---

## 5. Achieving Safe Extensibility

### 5.1 The Extensibility Contract

**✅ Safe to extend:**

- Register custom strategies for new pandas dtypes.
- Create custom Pydantic models that inherit from `BaseField` or `BaseReport`.
- Override `attributes_from_series()` to inject domain-specific metadata.

**❌ Do not modify:**

- The reserved attributes (`label`, `kind`, `required`, `description`).
- The core `Strategy` class API (`build_dict()`, `dtypes`, `type_name`).
- The shape of the top-level envelope (`{"inputs": [...], "outputs": [...]}`).

### 5.2 Example: Custom Strategy for Geospatial Data

```python
from typing import Literal
from pydantic import Field
from pandas import Series
from mlschema.core import BaseField, Strategy

# 1️⃣  Define the Pydantic schema
class LocationField(BaseField):
    kind: Literal["location"] = "location"
    latitude: float | None = None
    longitude: float | None = None
    zoom: int = 10

# 2️⃣  Define the Strategy
class LocationStrategy(Strategy):
    def __init__(self) -> None:
        super().__init__(
            type_name="location",
            schema_cls=LocationField,
            dtypes=("object",),
        )

    def attributes_from_series(self, series: Series) -> dict:
        return {
            "latitude": series.apply(extract_lat).mean(),
            "longitude": series.apply(extract_lon).mean(),
        }

# 3️⃣  Register it
mls = MLSchema()
mls.register(LocationStrategy())
```

Resulting schema:

```json
{
  "kind": "location",
  "label": "store_location",
  "required": true,
  "latitude": 40.7128,
  "longitude": -74.0060,
  "zoom": 12
}
```

---

## 6. Validation & Error Handling

### 6.1 Multi-Layer Validation

MLSchema enforces validation at three points:

1. **Strategy registration**: Ensures no dtype collisions or duplicate `type_name`s.
2. **DataFrame inspection**: Confirms all columns carry supported dtypes; raises if fallback is missing.
3. **Pydantic instantiation**: Validates field constraints (e.g., `min ≤ max`).

### 6.2 Exception Hierarchy

All library-level exceptions inherit from `mlschema.core.MLSchemaError`:

```python
try:
    schema = mls.build(df)
except mlschema.core.MLSchemaError as e:
    log.error(f"Schema generation failed: {e}")
```

Specific exceptions:

- `EmptyDataFrameError` – DataFrame has no rows or columns.
- `FallbackStrategyMissingError` – Unsupported dtype with no fallback.
- `StrategyNameAlreadyRegisteredError` – Duplicate `type_name` on `register()`.
- `StrategyDtypeAlreadyRegisteredError` – Duplicate dtype on `register()`.
- `ValidationError` (Pydantic) – Field constraint violation.

---

## 7. Best Practices for Schema Design

### 7.1 Pre-validation Checklist

Before calling `mls.build(df)`:

1. ✅ **Confirm dtypes**: Inspect `df.dtypes` to ensure columns carry the expected types.
2. ✅ **Handle nulls**: Decide whether columns should be `required: true` or `required: false`.
3. ✅ **Register strategies**: Only register the field types your application needs.
4. ✅ **Test edge cases**: Empty DataFrames, single rows, all-null columns.

### 7.2 Custom Strategy Patterns

1. **Inherit from `BaseField`**: Ensure your Pydantic model extends `BaseField`.
2. **Use `Literal` for `kind`**: Set `kind: Literal["custom_type"] = "custom_type"`.
3. **Override `attributes_from_series()` only**: Do not override `build_dict()` or other base methods.
4. **Validate early**: Use Pydantic `@model_validator` decorators to catch constraint violations at construction time.
5. **Respect reserved keys**: Do not emit `label`, `kind`, `required`, or `description` from `attributes_from_series()`.

---

## 8. Summary

MLSchema establishes a **data contract** that bridges machine learning models and consumer applications. By combining a strategy-driven architecture with rigorous Pydantic validation, the library achieves:

- **Reproducibility**: Same DataFrame → identical schema.
- **Extensibility**: Custom strategies plug in without core modifications.
- **Type Safety**: Literal annotations, Pydantic models, and static analysis.
- **Simplicity**: Sensible defaults; no configuration required for common dtypes.

---

**Next**: Refer to the [Usage Guide](usage.md) to implement your first custom strategy, or see the [API Reference](reference.md) for exhaustive method signatures.
