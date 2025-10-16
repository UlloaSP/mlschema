# Contributing to MLSchema

Thank you for considering contributing to MLSchema! 🎉

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Feature Requests](#feature-requests)
- [License](#license)

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please be respectful and constructive in all interactions.

### Our Standards

- **Be respectful**: Treat everyone with respect and kindness
- **Be collaborative**: Work together constructively
- **Be inclusive**: Welcome diverse perspectives
- **Be professional**: Keep discussions focused and productive

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:

   ```bash
   git clone https://github.com/YOUR_USERNAME/mlschema.git
   cd mlschema
   ```

3. **Add upstream remote**:

   ```bash
   git remote add upstream https://github.com/UlloaSP/mlschema.git
   ```

4. **Create a branch** for your changes:

   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

MLSchema uses [uv](https://docs.astral.sh/uv/) for dependency management.

### Prerequisites

- Python 3.14 or higher
- uv package manager

### Installation

1. **Install uv** (if not already installed):

   ```bash
   pip install uv
   ```

2. **Install dependencies**:

   ```bash
   uv sync
   ```

3. **Install pre-commit hooks**:

   ```bash
   uv run pre-commit install
   ```

### Project Structure

```text
mlschema/
├── src/mlschema/        # Main source code
│   ├── core/            # Core abstractions
│   │   ├── app/         # Application layer
│   │   ├── domain/      # Domain models
│   │   ├── exceptions/  # Custom exceptions
│   │   └── util/        # Utilities
│   └── strategies/      # Built-in strategies
├── test/                # Test suite
│   ├── integration/     # Integration tests
│   └── unit/            # Unit tests
├── docs/                # Documentation
└── pyproject.toml       # Project configuration
```

## Making Changes

### Branch Naming

Use descriptive branch names with prefixes:

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test improvements
- `chore/` - Maintenance tasks

Examples:

- `feature/add-boolean-strategy`
- `fix/handle-null-values`
- `docs/update-readme`

### Commit Messages

Follow conventional commits format:

```text
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/tooling changes

Examples:

```text
feat(strategies): add TimeDeltaStrategy for timedelta columns

fix(registry): handle duplicate dtype registration correctly

docs(readme): update installation instructions
```

## Testing

MLSchema uses pytest for testing. All code changes must include tests.

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest test/unit/test_mls.py

# Run specific test
uv run pytest test/unit/test_mls.py::TestMLSchemaInitialization::test_initialization_creates_field_service
```

### Test Requirements

- **Unit tests**: Test individual components in isolation
- **Integration tests**: Test real-world scenarios with actual DataFrames
- **Coverage**: Aim for 80% or higher code coverage
- **Mocking**: Use pytest-mock for external dependencies

### Writing Tests

```python
# Good test structure
def test_specific_behavior():
    """Test that X does Y when Z."""
    # Arrange
    strategy = NumberStrategy()
    series = Series([1, 2, 3], name="numbers")

    # Act
    result = strategy.build_dict(series)

    # Assert
    assert result["type"] == "number"
    assert result["step"] == 1
```

## Code Style

MLSchema uses modern Python tooling for code quality:

### Tools

- **Ruff**: Linting and formatting
- **Pyright**: Static type checking
- **pre-commit**: Automated checks before commits

### Running Checks

```bash
# Run all pre-commit hooks
uv run pre-commit run --all-files

# Run specific checks
uv run ruff check .
uv run ruff format .
uv run pyright
```

### Style Guidelines

- **Line length**: 88 characters (Black-compatible)
- **Quotes**: Double quotes `"` for strings
- **Imports**: Sorted with isort (via Ruff)
- **Type hints**: Required for all public APIs
- **Docstrings**: Google style for all public functions/classes

Example:

```python
def build_schema(dataframe: DataFrame, *, strict: bool = True) -> str:
    """Build a JSON schema from a pandas DataFrame.

    Args:
        dataframe: The DataFrame to convert to schema.
        strict: Whether to enforce strict validation.

    Returns:
        JSON string representing the schema.

    Raises:
        ValueError: If the DataFrame is empty.
    """
    ...
```

## Submitting Changes

### Pull Request Process

1. **Update your branch** with latest upstream:

   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run all checks**:

   ```bash
   uv run pre-commit run --all-files
   uv run pytest --cov=src --cov-fail-under=80
   ```

3. **Push to your fork**:

   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create a Pull Request** on GitHub

### PR Guidelines

- **Title**: Clear and descriptive (e.g., "Add DateStrategy for datetime columns")
- **Description**: Explain what and why
  - What does this PR do?
  - Why is this change needed?
  - How does it work?
  - Related issues (if any)
- **Tests**: Include new tests for your changes
- **Documentation**: Update docs if needed
- **Changelog**: Add entry to `docs/changelog.md`

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How was this tested?

## Checklist
- [ ] Tests pass locally
- [ ] Added/updated tests
- [ ] Added/updated documentation
- [ ] Pre-commit hooks pass
- [ ] Updated changelog
```

## Reporting Bugs

### Before Submitting

1. **Check existing issues** for duplicates
2. **Update to latest version** and test again
3. **Gather relevant information**

### Bug Report Template

```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Step one
2. Step two
3. ...

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., Windows 11, macOS 14]
- Python version: [e.g., 3.14.0]
- MLSchema version: [e.g., 0.1.1]
- pandas version: [e.g., 2.3.0]

## Additional Context
Screenshots, error messages, stack traces, etc.
```

## Feature Requests

We welcome feature requests! Please:

1. **Check existing issues** to avoid duplicates
2. **Describe the use case** clearly
3. **Explain the benefits**
4. **Propose an implementation** (optional)

### Feature Request Template

```markdown
## Feature Description
What feature would you like to see?

## Use Case
Why is this feature needed?

## Proposed Solution
How might this work?

## Alternatives Considered
What other approaches did you consider?

## Additional Context
Examples, mockups, references, etc.
```

## Development Guidelines

### Architecture Principles

1. **Strategy Pattern**: Each data type has its own strategy
2. **Opt-in**: Strategies must be explicitly registered
3. **Immutability**: Strategies don't mutate input data
4. **Validation**: Use Pydantic for schema validation
5. **Type Safety**: Full type hints with Pyright strict mode

### Adding a New Strategy

1. Create domain model in `src/mlschema/strategies/domain/`
2. Create strategy class in `src/mlschema/strategies/app/`
3. Register in `src/mlschema/strategies/__init__.py`
4. Add comprehensive tests
5. Update documentation

Example:

```python
from mlschema.core.app import Strategy
from mlschema.core.domain import BaseField

class CustomField(BaseField):
    """Custom field schema."""
    type: str = "custom"
    custom_attr: str | None = None

class CustomStrategy(Strategy):
    """Strategy for custom data type."""

    def __init__(self) -> None:
        super().__init__(
            type_name="custom",
            schema_cls=CustomField,
            dtypes=("custom_dtype",),
        )

    def attributes_from_series(self, series: Series) -> dict:
        """Extract custom attributes."""
        return {"custom_attr": "value"}
```

### Performance Considerations

- Avoid O(n²) algorithms on DataFrames
- Use pandas vectorized operations
- Don't load entire DataFrame into memory unnecessarily
- Cache expensive computations when appropriate

## Documentation

### Building Docs Locally

```bash
uv run mkdocs serve
```

Visit <http://127.0.0.1:8000> to view the documentation.

### Documentation Style

- Use clear, concise language
- Include code examples
- Add type hints to all code blocks
- Link to relevant API documentation

## Questions?

- **Discussions**: Use [GitHub Discussions](https://github.com/UlloaSP/mlschema/discussions)
- **Issues**: Report bugs via [GitHub Issues](https://github.com/UlloaSP/mlschema/issues)
- **Email**: Contact maintainers at <pablo.ulloa.santin@udc.es>

## License

By contributing to MLSchema, you agree that your contributions will be licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

Thank you for contributing to MLSchema! 🚀
