---
title: Python API
description: Signatures and contracts of every public MLschema symbol.
---

The package root exports the supported API:

```python
from mlschema import (
    BaseField,
    FieldBuilder,
    FieldContext,
    FieldDict,
    FieldKind,
    infer_schema,
    kind,
    with_positional_mappings,
)
```

Exceptions are exported from `mlschema.core`. Everything else is internal and can change without
notice.

## `infer_schema`

```python
def infer_schema(
    df: DataFrame,
    *,
    builders: Sequence[FieldBuilder] = (),
    kinds: Sequence[FieldKind] = (),
    overrides: Mapping[str, Mapping[str, Any]] | None = None,
    onehot_separator: str = "__",
) -> list[FieldDict]
```

Infers one validated field per DataFrame column, or per [one-hot group](/schema/mappings/#one-hot-groups).

| Parameter | Meaning |
| --- | --- |
| `df` | Source DataFrame. Must have at least one row and one column. |
| `builders` | Callables tried first, in order, for every column. See [Builders](/guides/extensions/#builders). |
| `kinds` | Custom kinds created with `kind()`. Their builders run after `builders` and before the built-ins. |
| `overrides` | Final patches keyed by column name, applied before validation. See [Overrides](/guides/overrides/). |
| `onehot_separator` | Separator between feature and value in one-hot column names. Must not be empty. |

Returns a JSON-serialisable `list[FieldDict]`, described in [Field contract](/schema/overview/).

Raises `EmptyDataFrameError`, `FieldKindAlreadyRegisteredError`, `FieldBuilderError`,
`UnknownFieldKindError`, or `pydantic.ValidationError`. See [Errors](/guides/errors/).

## `with_positional_mappings`

```python
def with_positional_mappings(
    fields: Sequence[FieldDict],
    feature_names: Sequence[str],
) -> list[FieldDict]
```

Returns a deep copy of `fields` in which each field's top-level `mappedTo`, or each option
`mappedTo` of an `onehot-category` field, is replaced by its index in `feature_names` when it is a
string. Integer targets already inside the range are kept. Labels, series columns, one-hot grouping
and other nested values are unchanged.

Raises `ValueError` for a string `feature_names`, empty, non-string, or duplicate names, a field
without a top-level `mappedTo` (other than `onehot-category`), a target missing from
`feature_names`, an out-of-range integer target, or a one-hot field without options.
See [Models that take a feature vector](/schema/mappings/#models-that-take-a-feature-vector).

## `kind`

```python
def kind(*, model: type[BaseField], infer: FieldBuilder) -> FieldKind
```

Creates a custom field kind. The kind name is the default of `model.kind`. Raises `FieldKindError`
when `model` is not a `BaseField` subclass, declares no `kind`, or defaults it to `None`. See
[Custom kinds](/guides/extensions/#custom-kinds).

## `BaseField`

Pydantic model that every field kind extends. It forbids undeclared attributes and defines the
[shared attributes](/schema/overview/#shared-attributes):

```python
class BaseField(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=False)

    label: Annotated[str, Field(min_length=1, max_length=100)]
    description: Annotated[str | None, Field(max_length=500)] = None
    required: bool = False
    mappedTo: Annotated[str, Field(min_length=1)] | Annotated[int, Field(ge=0)]
    valuePath: str | list[str] | None = None
    defaultValue: Any | None = None
```

## `FieldContext`

Frozen dataclass passed to every builder with the column's metadata: `name`, `dtype`, `required`,
`index`, `mappedTo`, and `infer_field`. The [FieldContext table](/guides/extensions/#fieldcontext)
describes each attribute.

## `FieldKind`

Frozen dataclass returned by `kind()`:

| Attribute | Type | Meaning |
| --- | --- | --- |
| `name` | `str` | Kind discriminator. |
| `model` | `type[BaseField]` | Model that validates and serialises the kind. |
| `infer` | `FieldBuilder` | Builder that emits fields of the kind. |

Create it with `kind()` so the name always matches the model.

## Type aliases

```python
type FieldDict = dict[str, Any]
type FieldBuilder = Callable[[Series, FieldContext], FieldDict | None]
```

## Exceptions

```python
from mlschema.core import (
    EmptyDataFrameError,
    FieldBuilderError,
    FieldKindAlreadyRegisteredError,
    FieldKindError,
    FieldServiceError,
    InvalidValueError,
    MLSchemaError,
    UnknownFieldKindError,
)
```

[Errors](/guides/errors/) shows the hierarchy, the attributes each exception carries, and when it is
raised.
