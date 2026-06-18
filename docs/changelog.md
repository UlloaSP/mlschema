# Changelog

All notable changes to MLSchema are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

No unreleased changes documented yet.

## [0.2.1] - 2026-06-18

### Added

* Added mandatory `mappedTo` output for normal fields.
* Added `onehot-category` inference for named one-hot encoded feature columns.
* Added `options[].mappedTo` targets for `onehot-category` options.
* Added `onehot_separator` to `infer_schema()`; the default separator is `"__"` for `feature__value` columns.
* Added positional-column fallback labels such as `feature_0`, `feature_1`, and integer `mappedTo` targets.

### Changed

* Changed named DataFrame columns to emit string `mappedTo` targets matching the column name.
* Changed positional DataFrame columns to emit generated labels and zero-based integer `mappedTo` targets.
* Changed one-hot grouping to require named encoded feature columns; positional binary columns now remain ordinary fields.
* Updated README, usage docs, and schema-standard docs for the `mappedTo` and `onehot-category` contracts.

### Fixed

* Fixed schema mapping ambiguity between display labels and backend targets.
* Fixed one-hot output so the parent field has no `mappedTo`; each option owns its backend target.
* Fixed regression coverage for named feature mappings, positional mappings, custom one-hot separators, and positional binary columns.

## [0.2.0] - 2026-06-01

`0.2.0` is a breaking release. MLSchema moves from the previous class-and-registry API to a smaller function-first API centred on `infer_schema(df)`. The schema output is now the field list itself, not a top-level object containing `fields`, `reports`, or `explanations`.

This release narrows the public surface, removes the report domain from MLSchema, and makes schema inference more direct for consumers that only need a validated field contract.

### Added

* Added the function-first public API:

  * `infer_schema`
  * `kind`
  * `BaseField`
  * `FieldBuilder`
  * `FieldContext`
  * `FieldDict`
  * `FieldKind`
* Added callable extension points through `builders=[...]`.
* Added strict custom kind registration through `kinds=[kind(model=..., infer=...)]`.
* Added default builtin inference for:

  * `series`
  * `boolean`
  * `category`
  * `date`
  * `number`
  * `text`
* Added explicit support for final field patches through `overrides={...}`.
* Added stricter inference exceptions for invalid builders, duplicate kinds, unknown kinds, invalid kind models, and missing override targets.
* Added pandas 3 dtype coverage for `str`, `datetime64[us]`, and `timedelta64[us]`.
* Added and expanded Google-style public docstrings for MkDocs API rendering.

### Changed

* Replaced the public `MLSchema()` orchestration workflow with `infer_schema(df)`.
* Changed schema generation to return `list[FieldDict]` directly.
* Changed builtin kinds to be enabled by default.
* Changed extension from class-based strategies to callable builders and strict custom kinds.
* Changed builder resolution to follow this order:

  * user builders
  * custom kind builders
  * builtin builders
* Changed field serialisation to use JSON mode with `exclude_none=True`.
* Changed documentation to describe the field-list contract as the canonical schema output.
* Changed tests to assert the direct field-list return contract.
* Split builtin builders and inference exceptions into focused modules.
* Consolidated the package version source into `pyproject.toml`.
* Consolidated Pyright configuration into `pyproject.toml`.
* Updated runtime dependencies:

  * `pandas >=3.0.3,<4.0.0`
  * `pydantic >=2.13.4,<3.0.0`
* Updated development tooling:

  * `pytest >=9.0.3`
  * `pytest-cov >=7.1.0`
  * `ruff >=0.15.15`
  * `pyright >=1.1.409`
  * `pre-commit >=4.6.0`
* Updated README, usage docs, schema standard, security notes, and third-party dependency documentation for the new public API.

### Removed

* Removed the public `MLSchema` facade.
* Removed public `Strategy`, `Registry`, `Service`, and strategy-class registration APIs.
* Removed public strategy classes from the supported documentation surface:

  * `TextStrategy`
  * `NumberStrategy`
  * `CategoryStrategy`
  * `BooleanStrategy`
  * `DateStrategy`
  * `SeriesStrategy`
* Removed class-based registration operations:

  * `register()`
  * `update()`
  * `unregister()`
  * `build()`
* Removed report-domain models from the public domain model:

  * `BaseReport`
  * `ClassifierReport`
  * `RegressorReport`
  * `ReportTypes`
* Removed generated `reports` and `explanations` members from schema output.
* Removed the top-level payload object used by earlier versions.
* Removed the duplicate `__version__` package constant.
* Removed `pyrightconfig.json`.

### Fixed

* Fixed pandas 3 dtype handling in builtin inference and tests.
* Fixed test expectations that still assumed the old top-level payload shape.
* Fixed documentation drift around the old registry and strategy APIs.
* Fixed version and type-checker configuration duplication.

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

## [0.1.6] - 2026-04-21

### Added

* Added `explanations` to the top-level schema payload.

### Changed

* Updated README and documentation to describe the `fields`, `reports`, and `explanations` payload shape.
* Bumped package version to `0.1.6`.

## [0.1.5] - 2026-04-17

### Changed

* Renamed the top-level schema payload from `inputs` and `outputs` to `fields` and `reports`.
* Updated README, schema standard, usage docs, service output, and integration tests for the renamed payload members.
* Bumped package version to `0.1.5`.

## [0.1.4] - 2026-04-17

### Added

* Added report-domain models:

  * `BaseReport`
  * `ClassifierReport`
  * `RegressorReport`
  * `ReportTypes`

### Changed

* Refactored field schemas to use `kind` as the type discriminator.
* Renamed field defaults to `defaultValue`.
* Expanded `BaseField` with UI and state metadata.
* Added inactive-field behaviour to the base field contract.
* Updated builtin strategies, documentation, and tests for the revised field attribute contract.
* Bumped package version to `0.1.4`.

## [0.1.3] - 2026-04-16

### Added

* Added `SeriesStrategy` for content-based detection of two-axis compound columns.
* Added `SeriesField` with `field1`, `field2`, `minPoints`, and `maxPoints`.
* Added `add_series_sub_field()` for custom series subfield registration.
* Added `Strategy.content_probe()` for content-based strategy matching.
* Added `Strategy.set_registry()` for registry-aware strategies.
* Added `Registry.strategy_for_content()` for content-driven lookup.
* Added the first schema-standard documentation page.

### Changed

* Updated service field generation to prefer content-probe matches before dtype lookup and text fallback.
* Exported `SeriesStrategy` and `add_series_sub_field()` from the public strategies API.
* Updated README and usage docs with series-column examples and constraints.
* Bumped package version to `0.1.3`.

## [0.1.2] - 2025-10-29

### Added

* Added SPDX license headers across source and test files.

### Changed

* Reworked README content and project documentation.
* Updated documentation after the `0.1.1` release.
* Bumped package version to `0.1.2`.

## [0.1.1] - 2025-10-16

### Added

* Added the initial `MLSchema` facade with `register`, `unregister`, `update`, and `build` operations.
* Added registry, service, and strategy application layers.
* Added Pydantic field schemas for:

  * boolean fields
  * number fields
  * text fields
  * date fields
  * category fields
* Added builtin strategies for common pandas dtypes.
* Added typed domain, exception, and utility modules.
* Added unit and integration tests.
* Added MkDocs documentation.
* Added README content, installation guide, usage guide, and issue templates.
* Added GitHub Actions CI, publishing workflow, pre-commit hooks, and project metadata.

### Changed

* Changed schema generation to return dictionaries instead of JSON strings.
* Refactored strategy classes around a unified `Strategy` base class.
* Updated CI dependency installation to use `uv`.
* Updated README and documentation for package usage and release workflow.
* Bumped package version to `0.1.1`.
