# Changelog

All notable changes to MLSchema will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-10-08

### Added

- Initial release of MLSchema
- Core `MLSchema` class with register, unregister, update, and build methods
- Strategy pattern architecture for extensible field type handling
- Built-in strategies:
  - `NumberStrategy`: Handles int32, int64, float32, float64
  - `TextStrategy`: Handles object and string types
  - `BooleanStrategy`: Handles bool and boolean types
  - `DateStrategy`: Handles datetime64[ns] types
  - `CategoryStrategy`: Handles categorical types
- Pydantic-based schema validation
- Comprehensive test suite (281 tests, 100% coverage)
- Full type hints with Pyright strict mode
- Documentation with MkDocs
- Pre-commit hooks for code quality

### Changed

N/A

### Deprecated

N/A

### Removed

N/A

### Fixed

N/A

### Security

N/A

---
## [0.1.2] - 2025-10-29

### Added

- Open Software License Headers

### Changed

- Readme

### Deprecated

N/A

### Removed

N/A

### Fixed

N/A

### Security

N/A

## [0.1.3] - 2026-04-16

### Added

- `SeriesStrategy`: content-based strategy for two-axis columns. Each cell must be a 2-element tuple, list, or dict. Sub-field schemas are auto-inferred from element dtypes via the registered strategy registry.
- `SeriesField`: Pydantic model for series fields with `field1`, `field2`, `min_points`, and `max_points` attributes.
  - `field1` / `field2` accept any registered sub-field type; nesting `SeriesField` inside itself is explicitly rejected.
  - `min_points` / `max_points` enforce cardinality constraints (`PositiveInt`; `min_points ≤ max_points`).
- `add_series_sub_field(cls)`: public helper to register custom `BaseField` subclasses as valid sub-fields inside `SeriesField`.
- `content_probe(series)` hook on `Strategy` base class (default `False`). Strategies that override this are matched **before** dtype-based lookup, enabling non-dtype detection patterns.
- `set_registry(registry)` hook on `Strategy` base class (no-op default). Called by `Service.register()` after registration. `SeriesStrategy` uses it to access the registry for sub-field dtype resolution.
- `Registry.strategy_for_content(series)`: iterates registered strategies and returns the first whose `content_probe()` returns `True`.

### Changed

- `Service._field_payload()`: content-probe lookup now takes priority over dtype and fallback lookups.
- `FieldTypes` enum: added `SERIES = "series"`.
- `strategies` public API: `SeriesStrategy` and `add_series_sub_field` now exported at package level.

### Fixed

N/A

### Security

N/A

---

**Legend:**

- 🎉 **Added**: New features
- 🔄 **Changed**: Changes in existing functionality
- 🗑️ **Deprecated**: Soon-to-be removed features
- ❌ **Removed**: Now removed features
- 🐛 **Fixed**: Bug fixes
- 🔒 **Security**: Security improvements

---

**Last Updated**: April 16, 2026
