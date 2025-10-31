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

Every field in an MLSchema schema carries four **reserved** attributes, defined by the `BaseField` Pydantic model:

| Attribute     | Type         | Constraint              | Example              |
|---------------|--------------|------------------------|----------------------|
| `title`       | `str`        | 1–100 characters       | `"Age"`              |
| `description` | `str \| None`| max 500 characters     | `"Customer age"`     |
| `required`    | `bool`       | Derived from nullability| `true`               |
| `type`        | `str`        | Strategy-specific      | `"text"`, `"number"` |

These attributes are **immutable** and **reserved**. Custom strategies must not override them; instead, they augment the base contract with domain-specific keys.

### 2.3 Domain-Specific Extensions

Each strategy introduces optional attributes that refine the field contract. For example:

- **NumberField**: `min`, `max`, `step`, `unit`, `placeholder`, `value`
- **TextField**: `minLength`, `maxLength`, `pattern`, `placeholder`, `value`
- **CategoryField**: `options`, `value`
- **DateField**: `min`, `max`, `step`, `value`

These extensions are **not** free-form; they are rigorously typed and validated by Pydantic models. This ensures that consumers can safely parse and reason about the schema at runtime.

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
      "title": "customer_name",
      "type": "text",
      "required": true,
      "description": "Full name of the customer",
      "minLength": 1,
      "maxLength": 100,
      "placeholder": "Enter full name"
    },
    {
      "title": "satisfaction_score",
      "type": "number",
      "required": true,
      "description": "Customer satisfaction (0–100)",
      "min": 0,
      "max": 100,
      "step": 1,
      "unit": "points"
    }
  ],
  "outputs": []
}
```

The top-level envelope (`inputs`, `outputs`) provides logical separation between model parameters and expected predictions, facilitating schema validation at both entry and exit boundaries.

### 3.2 Field Type Taxonomy

MLSchema ships with five built-in field types, each with a distinct Pydantic model and serialization contract:

#### **Type: `text`**

Represents string data. Backend validation includes length constraints and regex patterns.

```json
{
  "type": "text",
  "title": "email",
  "required": true,
  "description": "User email address",
  "minLength": 5,
  "maxLength": 254,
  "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
  "placeholder": "user@example.com"
}
```

**Supported pandas dtypes**: `object`, `string`

#### **Type: `number`**

Represents numeric data (int or float). Backend validation enforces min/max bounds and step increments.

```json
{
  "type": "number",
  "title": "revenue",
  "required": true,
  "description": "Quarterly revenue in USD",
  "min": 0,
  "max": 1000000,
  "step": 0.01,
  "unit": "USD",
  "placeholder": "Enter amount"
}
```

**Supported pandas dtypes**: `int64`, `float64`, `int32`, `float32`

#### **Type: `category`**

Represents enumerated, finite sets of values. The `options` key is mandatory and is automatically derived from the DataFrame's unique categorical values.

```json
{
  "type": "category",
  "title": "customer_segment",
  "required": true,
  "description": "Customer loyalty tier",
  "options": ["Bronze", "Silver", "Gold"],
  "value": "Silver"
}
```

**Supported pandas dtypes**: `category`

#### **Type: `boolean`**

Represents binary (true/false) data.

```json
{
  "type": "boolean",
  "title": "is_active",
  "required": true,
  "description": "Account is active and verified",
  "value": true
}
```

**Supported pandas dtypes**: `bool`, `boolean`

#### **Type: `date`**

Represents temporal data. Backend validation ensures `min ≤ max` and `value ∈ [min, max]`.

```json
{
  "type": "date",
  "title": "contract_renewal",
  "required": false,
  "description": "Target contract renewal date",
  "min": "2024-01-01",
  "max": "2026-12-31",
  "step": 7,
  "value": "2025-06-15"
}
```

**Supported pandas dtypes**: `datetime64[ns]`, `datetime64`

---

## 4. Design Decisions & Rationale

### 4.1 Why Pydantic?

Pydantic v2 provides:

1. **Type safety**: Schemas are validated at construction time, not at serialization.
2. **Composability**: Custom models inherit from `BaseField`, enabling incremental extension without duplication.
3. **Standard format**: Pydantic models emit JSON in a deterministic, language-agnostic format.
4. **Validators**: Embedded, reusable validation logic (e.g., `min ≤ max`, regex patterns).

### 4.2 Why a Literal Type Annotation?

The `type` field in each Pydantic model uses Python's `Literal` type:

```python
class NumberField(BaseField):
    type: Literal[FieldTypes.NUMBER] = FieldTypes.NUMBER
```

This choice ensures:

- **Type narrowing**: IDEs and static analyzers can discriminate on the `type` field.
- **Exhaustiveness**: Consumer code can enforce complete handling of all field types.
- **No collisions**: Only one schema matches a given `type` string, preventing silent overwrites.

### 4.3 Why Reserved Keys?

The four reserved keys (`title`, `type`, `required`, `description`) are **always** populated by the base `Strategy` class. Custom strategies cannot override them. This ensures:

1. **Predictability**: Consumers know these keys will always be present and meaningful.
2. **Schema integrity**: The contract is never violated by careless implementations.
3. **Versioning safety**: Future MLSchema versions can extend reserved keys without breaking custom strategies.

### 4.4 Why `exclude_none=True`?

Pydantic's serialization mode `exclude_none=True` strips `null` values from the JSON output:

```json
{
  "type": "text",
  "minLength": 1,
  "maxLength": 100
  // "placeholder": null is excluded
}
```

This keeps payloads compact and simplifies consumer logic (no need to check for null default values). Optional attributes are **omitted** when not set, not serialized as `null`.

---

## 5. Achieving Safe Extensibility

### 5.1 The Extensibility Contract

MLSchema is designed with a clear **extension boundary**:

**✅ Safe to extend:**

- Register custom strategies for new pandas dtypes.
- Create custom Pydantic models that inherit from `BaseField`.
- Override `attributes_from_series()` to inject domain-specific metadata.

**❌ Do not modify:**

- The four reserved attributes (`title`, `type`, `required`, `description`).
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
    type: Literal["location"] = "location"  # Custom type
    latitude: float | None = None
    longitude: float | None = None
    zoom: int = 10

# 2️⃣  Define the Strategy
class LocationStrategy(Strategy):
    def __init__(self) -> None:
        super().__init__(
            type_name="location",
            schema_cls=LocationField,
            dtypes=("object",),  # Assume WKT or GeoJSON strings
        )

    def attributes_from_series(self, series: Series) -> dict:
        # Parse geospatial data and extract centroid
        return {
            "latitude": series.apply(extract_lat).mean(),
            "longitude": series.apply(extract_lon).mean(),
        }

# 3️⃣  Register it
mls = MLSchema()
mls.register(LocationStrategy())
```

The resulting schema is fully compatible with existing MLSchema tooling:

```json
{
  "type": "location",
  "title": "store_location",
  "required": true,
  "description": "Physical store coordinates",
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
3. **Pydantic instantiation**: Validates field constraints (e.g., `min ≤ max`, value in range).

### 6.2 Exception Hierarchy

All library-level exceptions inherit from `mlschema.core.MLSchemaError`:

```python
try:
    schema = mls.build(df)
except mlschema.core.MLSchemaError as e:
    # All MLSchema-specific errors
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

When adding custom strategies:

1. **Inherit from `BaseField`**: Ensure your Pydantic model extends `BaseField`.
2. **Use `Literal` for `type`**: Set `type: Literal["custom_type"] = "custom_type"`.
3. **Override `attributes_from_series()` only**: Do not override `build_dict()` or other base methods.
4. **Validate early**: Use Pydantic `@model_validator` decorators to catch constraint violations at construction time.
5. **Document reserved keys**: Remind users that `title`, `type`, `required`, `description` are off-limits.

---

## 8. Roadmap & Future Extensions

MLSchema is designed for evolution. Planned or under consideration:

- **Nested schemas**: Support for DataFrame columns containing structured data (dicts, lists).
- **Conditional validation**: Rules that depend on sibling field values.
- **Localization**: Multi-language titles and descriptions.
- **UI hints**: Metadata for custom renderers (CSS classes, icons, tooltips).
- **Audit trail**: Provenance tracking for schema changes.

All extensions will respect the core design principles: strategy-driven, Pydantic-validated, type-safe, and backward-compatible.

---

## 9. Summary

MLSchema establishes a **data contract** that bridges machine learning models and consumer applications. By combining a strategy-driven architecture with rigorous Pydantic validation, the library achieves:

- **Reproducibility**: Same DataFrame → identical schema.
- **Extensibility**: Custom strategies plug in without core modifications.
- **Type Safety**: Literal annotations, Pydantic models, and static analysis.
- **Simplicity**: Sensible defaults; no configuration required for common dtypes.

The standard is not prescriptive; it is **enabling**. It gives teams the tools to build reproducible, governable, and scalable ML inference pipelines.

---

**Next**: Refer to the [Usage Guide](usage.md) to implement your first custom strategy, or see the [API Reference](reference.md) for exhaustive method signatures.
