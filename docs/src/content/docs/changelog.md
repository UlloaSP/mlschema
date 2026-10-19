---
title: Changelog
description: Every notable change to MLschema, newest first, with migration notes for breaking releases.
---

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project
follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Versions before 1.0 may change
the field contract in a minor release. Releases `0.1.1` to `0.1.6` are in the
[0.1 history](/changelog/0-1/).

## [0.3.0] - Unreleased

`0.3.0` is prepared but not yet published. It is a breaking release for `series` fields.

### Added

- Added `with_positional_mappings(fields, feature_names)`. It returns a deep copy of an inferred
  schema with each field's top-level `mappedTo`, and each `onehot-category` option's `mappedTo`,
  replaced by its position in `feature_names`. Existing in-range integer targets are kept; labels, series columns and
  one-hot grouping are unchanged. It raises `ValueError` for duplicate, empty or non-string feature
  names and for unknown or out-of-range targets.

### Changed

- **Breaking:** `series` fields emit `columns`, a list of exactly two column objects with ids
  `field1` and `field2`, instead of the `field1` and `field2` attributes.
- **Breaking:** series columns carry no `mappedTo`. The series keeps its own top-level `mappedTo`.
- Series columns accept only scalar kinds: `text`, `number`, `date`, `category`, `boolean`, and
  custom scalar kinds. `series` and `onehot-category` are rejected as columns.
- Moved the documentation to an Astro Starlight site at <https://docs.mlschema.eshkra.dev/>.

### Removed

- Removed the MkDocs configuration and the `docs` Python dependency group.

### Migration notes

Read series columns from the list instead of the two attributes:

```diff
- time = field["field1"]
- value = field["field2"]
+ time, value = field["columns"]
```

Each column now has an `id` (`field1` or `field2`) and no `mappedTo`. Consumers that sent a series
cell by a column's `mappedTo` must send rows under the series `mappedTo`, keyed by column id. The
shape matches [MLForm series](https://docs.mlform.eshkra.dev/schema/series/). Builders, kinds and
overrides that produce series fields must emit `columns` in the same form.

Code that rewrote named targets into model input positions after inference can call
`with_positional_mappings(fields, feature_names)` instead.

Upgrading from `0.2.0` or earlier also requires the `0.2.1` changes: custom builders must return
`"mappedTo": ctx.mappedTo`, and one-hot groups map through their options. The `0.2.0` migration
notes below predate `mappedTo`; add it to the builder examples there.

## [0.2.1] - 2026-06-18

### Added

- Added mandatory `mappedTo` output for normal fields.
- Added `onehot-category` inference for named one-hot encoded feature columns.
- Added `options[].mappedTo` targets for `onehot-category` options.
- Added `onehot_separator` to `infer_schema()`; the default separator is `"__"` for `feature__value` columns.
- Added positional-column fallback labels such as `feature_0`, `feature_1`, and integer `mappedTo` targets.

### Changed

- Changed named DataFrame columns to emit string `mappedTo` targets matching the column name.
- Changed positional DataFrame columns to emit generated labels and zero-based integer `mappedTo` targets.
- Changed one-hot grouping to require named encoded feature columns; positional binary columns now remain ordinary fields.
- Updated README, usage docs, and schema-standard docs for the `mappedTo` and `onehot-category` contracts.

### Fixed

- Fixed schema mapping ambiguity between display labels and backend targets.
- Fixed one-hot output so the parent field has no `mappedTo`; each option owns its backend target.
- Fixed regression coverage for named feature mappings, positional mappings, custom one-hot separators, and positional binary columns.

## [0.2.0] - 2026-06-01

`0.2.0` is a breaking release. MLschema moves from the previous class-and-registry API to a smaller function-first API centred on `infer_schema(df)`. The schema output is now the field list itself, not a top-level object containing `fields`, `reports`, or `explanations`.

This release narrows the public surface, removes the report domain from MLschema, and makes schema inference more direct for consumers that only need a validated field contract.

### Added

- Added the function-first public API:
  - `infer_schema`
  - `kind`
  - `BaseField`
  - `FieldBuilder`
  - `FieldContext`
  - `FieldDict`
  - `FieldKind`
- Added callable extension points through `builders=[...]`.
- Added strict custom kind registration through `kinds=[kind(model=..., infer=...)]`.
- Added default builtin inference for:
  - `series`
  - `boolean`
  - `category`
  - `date`
  - `number`
  - `text`
- Added explicit support for final field patches through `overrides={...}`.
- Added stricter inference exceptions for invalid builders, duplicate kinds, unknown kinds, invalid kind models, and missing override targets.
- Added pandas 3 dtype coverage for `str`, `datetime64[us]`, and `timedelta64[us]`.
- Added and expanded Google-style public docstrings for MkDocs API rendering.

### Changed

- Replaced the public `MLSchema()` orchestration workflow with `infer_schema(df)`.
- Changed schema generation to return `list[FieldDict]` directly.
- Changed builtin kinds to be enabled by default.
- Changed extension from class-based strategies to callable builders and strict custom kinds.
- Changed builder resolution to follow this order:
  - user builders
  - custom kind builders
  - builtin builders
- Changed field serialisation to use JSON mode with `exclude_none=True`.
- Changed documentation to describe the field-list contract as the canonical schema output.
- Changed tests to assert the direct field-list return contract.
- Split builtin builders and inference exceptions into focused modules.
- Consolidated the package version source into `pyproject.toml`.
- Consolidated Pyright configuration into `pyproject.toml`.
- Updated runtime dependencies:
  - `pandas >=3.0.3,<4.0.0`
  - `pydantic >=2.13.4,<3.0.0`
- Updated development tooling:
  - `pytest >=9.0.3`
  - `pytest-cov >=7.1.0`
  - `ruff >=0.15.15`
  - `pyright >=1.1.409`
  - `pre-commit >=4.6.0`
- Updated README, usage docs, schema standard, security notes, and third-party dependency documentation for the new public API.

### Removed

- Removed the public `MLSchema` facade.
- Removed public `Strategy`, `Registry`, `Service`, and strategy-class registration APIs.
- Removed public strategy classes from the supported documentation surface:
  - `TextStrategy`
  - `NumberStrategy`
  - `CategoryStrategy`
  - `BooleanStrategy`
  - `DateStrategy`
  - `SeriesStrategy`
- Removed class-based registration operations:
  - `register()`
  - `update()`
  - `unregister()`
  - `build()`
- Removed report-domain models from the public domain model:
  - `BaseReport`
  - `ClassifierReport`
  - `RegressorReport`
  - `ReportTypes`
- Removed generated `reports` and `explanations` members from schema output.
- Removed the top-level payload object used by earlier versions.
- Removed the duplicate `__version__` package constant.
- Removed `pyrightconfig.json`.

### Fixed

- Fixed pandas 3 dtype handling in builtin inference and tests.
- Fixed test expectations that still assumed the old top-level payload shape.
- Fixed documentation drift around the old registry and strategy APIs.
- Fixed version and type-checker configuration duplication.

### Migration Notes

Replace the old orchestrator workflow:

```python
from mlschema import MLSchema
from mlschema.strategies import TextStrategy

schema_builder = MLSchema()
schema_builder.register(TextStrategy())

schema = schema_builder.build(df)
```

with the new public API:

```python
from mlschema import infer_schema

schema = infer_schema(df)
```

Replace custom strategy classes with callable builders when the target kind already exists:

```python
from pandas import Series

from mlschema import FieldContext, infer_schema


def money_builder(series: Series, ctx: FieldContext) -> dict | None:
    if ctx.name != "amount_eur":
        return None

    return {
        "kind": "number",
        "label": "Amount",
        "required": ctx.required,
        "step": 0.01,
        "unit": "EUR",
        "min": 0,
    }


schema = infer_schema(df, builders=[money_builder])
```

Use `kind()` only when the schema needs a new field discriminator and a dedicated Pydantic model:

```python
from typing import Literal

from pandas import Series

from mlschema import BaseField, FieldContext, infer_schema, kind


class DurationField(BaseField):
    kind: Literal["duration"] = "duration"
    unit: Literal["seconds"] = "seconds"
    minSeconds: int
    maxSeconds: int


def duration_builder(series: Series, ctx: FieldContext) -> dict | None:
    if ctx.dtype not in {"timedelta64[ns]", "timedelta64[us]"}:
        return None

    return {
        "kind": "duration",
        "label": ctx.name,
        "required": ctx.required,
        "unit": "seconds",
        "minSeconds": int(series.min().total_seconds()),
        "maxSeconds": int(series.max().total_seconds()),
    }


schema = infer_schema(
    df,
    kinds=[
        kind(model=DurationField, infer=duration_builder),
    ],
)
```

If previous consumers expected a top-level payload such as:

```json
{
  "fields": [],
  "reports": [],
  "explanations": []
}
```

they must now consume the field list directly:

```json
[
  {
    "kind": "text",
    "label": "name",
    "required": true
  }
]
```

Applications that still need an envelope should create it at the application boundary.
