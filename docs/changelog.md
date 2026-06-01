# Changelog

All notable changes to MLSchema will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-06-01

### Changed

- Changed `MLSchema.build()` / `Service.build_schema()` to return the field schema list directly instead of a top-level payload object.
- Updated runtime dependencies to pandas `>=3.0.3,<4.0.0` and pydantic `>=2.13.4,<3.0.0`.
- Updated development tooling: pytest `>=9.0.3`, pytest-cov `>=7.1.0`, ruff `>=0.15.15`, pyright `>=1.1.409`, pre-commit `>=4.6.0`.
- Consolidated package version source into `pyproject.toml`; CI publish reads the version from there.
- Consolidated Pyright configuration into `pyproject.toml`.
- Updated docs, README, security notes, and third-party dependency documentation for the new field-list contract and dependency versions.

### Removed

- Removed `BaseReport`, `ClassifierReport`, `RegressorReport`, and `ReportTypes` from the public domain model.
- Removed generated `reports` and `explanations` payload members from schema output.
- Removed duplicate `__version__` package constant.
- Removed `pyrightconfig.json`.

### Fixed

- Registered pandas 3 dtype names (`str`, `datetime64[us]`, `timedelta64[us]`) on the strategies/tests that own those dtype contracts.
- Updated tests to assert the direct field-list return contract.

## [0.1.6] - 2026-04-21

### Added

- Added `explanations` to the top-level schema payload.

### Changed

- Updated README and docs to document the `fields` / `reports` / `explanations` payload shape.
- Bumped package version to `0.1.6`.

## [0.1.5] - 2026-04-17

### Changed

- Renamed the top-level schema payload from `inputs` / `outputs` to `fields` / `reports`.
- Updated README, schema standard, usage docs, service output, and integration tests for the new payload names.
- Bumped package version to `0.1.5`.

## [0.1.4] - 2026-04-17

### Added

- Added report-domain models: `BaseReport`, `ClassifierReport`, `RegressorReport`, and `ReportTypes`.

### Changed

- Refactored field schemas to use `kind` as the type discriminator.
- Renamed field defaults to `defaultValue`.
- Expanded `BaseField` with UI/state metadata and inactive-field behavior.
- Updated built-in strategies, docs, and tests for the new field attribute contract.
- Bumped package version to `0.1.4`.

## [0.1.3] - 2026-04-16

### Added

- Added `SeriesStrategy` for content-based detection of two-axis compound columns.
- Added `SeriesField` with `field1`, `field2`, `minPoints`, and `maxPoints`.
- Added `add_series_sub_field()` for custom sub-field registration.
- Added `Strategy.content_probe()` and `Strategy.set_registry()` hooks.
- Added `Registry.strategy_for_content()` for content-driven strategy lookup.
- Added schema-standard documentation.

### Changed

- Updated `Service._field_payload()` to prefer content-probe matches before dtype and text fallback lookup.
- Exported `SeriesStrategy` and `add_series_sub_field` from the public strategies API.
- Updated README and usage docs with series-column examples and constraints.
- Bumped package version to `0.1.3`.

## [0.1.2] - 2025-10-29

### Added

- Added SPDX license headers across source and test files.

### Changed

- Reworked README content and project documentation.
- Updated docs after the `0.1.1` release.
- Bumped package version to `0.1.2`.

## [0.1.1] - 2025-10-16

### Added

- Added MLSchema facade with register, unregister, update, and build operations.
- Added registry, service, and strategy application layers.
- Added Pydantic field schemas for boolean, number, text, date, and category fields.
- Added built-in strategies for boolean, number, text, date, and category pandas dtypes.
- Added typed domain, exception, and utility modules.
- Added comprehensive unit and integration tests.
- Added MkDocs documentation, README content, installation guide, usage guide, and issue templates.
- Added GitHub Actions CI, publishing workflow, pre-commit hooks, and project metadata.

### Changed

- Changed schema generation to return dictionaries instead of JSON strings.
- Refactored strategy classes around a unified `Strategy` base class.
- Updated CI dependency installation to use `uv`.
- Updated README and documentation for package usage and release workflow.
- Bumped package version to `0.1.1`.

**Last Updated**: June 1, 2026
