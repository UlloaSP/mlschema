# Changelog

All notable changes to MLSchema will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Comprehensive project documentation
- THIRD_PARTY_LICENSES.md with all dependency licenses
- CONTRIBUTING.md with contribution guidelines
- SECURITY.md with security policy and disclosure process
- AUTHORS.md recognizing contributors
- Enhanced pyproject.toml with license, classifiers, and URLs

### Changed

- Removed explicit NumPy dependency (now accessed through pandas)
- Updated all tests to use pandas APIs instead of NumPy

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
- Comprehensive test suite (279 tests, 95%+ coverage)
- Full type hints with Pyright strict mode
- Documentation with MkDocs
- Pre-commit hooks for code quality

### Core Features

- **Opt-in Strategy System**: Strategies must be explicitly registered
- **Type Safety**: Full type hints and validation
- **Extensibility**: Easy to add custom strategies
- **Validation**: Pydantic ensures schema correctness
- **Immutability**: Strategies never modify input DataFrames

### Documentation

- Installation guide
- Usage examples
- API reference
- Architecture overview
- Strategy development guide

### Development Tools

- UV for dependency management
- Ruff for linting and formatting
- Pyright for static type checking
- pytest for testing
- pre-commit for automated checks
- GitHub Actions CI/CD pipeline

## Release Notes

### Version 0.1.1 Highlights

This is the first public release of MLSchema, a micro-library for converting pandas DataFrames into JSON schemas.

**Key Features:**

- 🎯 **Strategy Pattern**: Flexible, extensible architecture
- 🔒 **Type Safe**: Full type hints with Pyright
- ✅ **Validated**: Pydantic ensures correctness
- 🧪 **Well Tested**: 279 tests, 80%+ coverage
- 📚 **Documented**: Comprehensive docs with examples
- 🚀 **Production Ready**: Used in real-world projects

**Quick Start:**

```python
import pandas as pd
from mlschema import MLSchema
from mlschema.strategies.app import NumberStrategy, TextStrategy

# Create a DataFrame
df = pd.DataFrame({
    "age": [25, 30, 35],
    "name": ["Alice", "Bob", "Charlie"]
})

# Generate schema
ml_schema = MLSchema()
ml_schema.register(NumberStrategy())
ml_schema.register(TextStrategy())

schema = ml_schema.build(df)
print(schema)
```

## Migration Guides

### From Pre-release Versions

If you were using a pre-release version:

1. Update your imports:

   ```python
   # Old (if you used internal APIs)
   from mlschema.core.app.field_strategy import FieldStrategy

   # New
   from mlschema.core.app.strategy import Strategy
   ```

2. All built-in strategies are now in `mlschema.strategies.app`

3. Run your tests to ensure compatibility

## Deprecations

None in this release.

## Breaking Changes

None in this release (first public version).

## Known Issues

- Very large DataFrames (>1M rows) may have performance considerations
- Complex nested data structures are not yet supported
- Timezone-aware datetime handling is basic

See [Issues](https://github.com/UlloaSP/mlschema/issues) for the full list.

## Future Plans

### Planned for 0.2.0

- [ ] Additional built-in strategies (TimeDelta, Period, etc.)
- [ ] Performance optimizations for large DataFrames
- [ ] Enhanced datetime timezone support
- [ ] Schema versioning and migration tools

### Under Consideration

- Schema diff and comparison tools
- Schema merging capabilities
- Schema to DataFrame reverse conversion
- Plugin system for third-party strategies
- CLI tool for schema generation

See [Roadmap](https://github.com/UlloaSP/mlschema/projects) for more details.

## Contributors

Thanks to all contributors who helped make this release possible!

See [AUTHORS.md](AUTHORS.md) for the full list of contributors.

## Links

- [GitHub Repository](https://github.com/UlloaSP/mlschema)
- [Documentation](https://ulloasp.github.io/mlschema/)
- [PyPI Package](https://pypi.org/project/mlschema/)
- [Issue Tracker](https://github.com/UlloaSP/mlschema/issues)

---

**Legend:**

- 🎉 **Added**: New features
- 🔄 **Changed**: Changes in existing functionality
- 🗑️ **Deprecated**: Soon-to-be removed features
- ❌ **Removed**: Now removed features
- 🐛 **Fixed**: Bug fixes
- 🔒 **Security**: Security improvements

---

**Last Updated**: October 8, 2025
