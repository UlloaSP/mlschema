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

---

**Legend:**

- 🎉 **Added**: New features
- 🔄 **Changed**: Changes in existing functionality
- 🗑️ **Deprecated**: Soon-to-be removed features
- ❌ **Removed**: Now removed features
- 🐛 **Fixed**: Bug fixes
- 🔒 **Security**: Security improvements

---

**Last Updated**: October 29, 2025
