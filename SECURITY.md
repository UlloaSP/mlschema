# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

We take the security of MLSchema seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Please Do NOT

- **Do not** open a public GitHub issue for security vulnerabilities
- **Do not** disclose the vulnerability publicly until it has been addressed

### Please DO

1. **Email us directly** at: <pablo.ulloa.santin@udc.es>
2. **Include the following information**:
   - Type of vulnerability
   - Full paths of source file(s) related to the manifestation of the vulnerability
   - The location of the affected source code (tag/branch/commit or direct URL)
   - Any special configuration required to reproduce the issue
   - Step-by-step instructions to reproduce the issue
   - Proof-of-concept or exploit code (if possible)
   - Impact of the issue, including how an attacker might exploit it

### What to Expect

- **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 48 hours
- **Communication**: We will keep you informed about the progress of the fix
- **Timeline**: We aim to address critical vulnerabilities within 30 days
- **Credit**: With your permission, we will publicly acknowledge your responsible disclosure

## Security Best Practices

When using MLSchema, we recommend:

### Input Validation

```python
from pandas import DataFrame
from mlschema import MLSchema

# Always validate DataFrame input
if not isinstance(df, DataFrame):
    raise TypeError("Expected pandas DataFrame")

if df.empty:
    raise ValueError("DataFrame cannot be empty")

# Use MLSchema with proper error handling
ml_schema = MLSchema()
try:
    schema = ml_schema.build(df)
except Exception as e:
    # Handle errors appropriately
    logging.error(f"Schema generation failed: {e}")
```

### Dependency Management

- Keep dependencies up to date
- Use `uv sync` to ensure consistent versions
- Monitor security advisories for pandas and Pydantic

### Safe Data Handling

```python
# Don't expose sensitive data in schemas
df = df.drop(columns=["password", "api_key", "secret"])

# Sanitize column names if needed
df.columns = [col.replace(" ", "_").lower() for col in df.columns]
```

## Security Considerations

### Data Processing

MLSchema processes pandas DataFrames to generate JSON schemas. It:

- **Does not** modify the original DataFrame
- **Does not** send data over the network
- **Does not** write data to disk
- **Does not** execute arbitrary code from DataFrame contents

### Type Safety

MLSchema uses Pydantic for validation, which provides:

- Type checking and validation
- Protection against invalid data structures
- Clear error messages for malformed input

### Known Limitations

- MLSchema assumes DataFrames come from trusted sources
- Column names are used as-is in the output schema
- Very large DataFrames may cause memory issues

## Vulnerability Disclosure Policy

We follow a **coordinated disclosure** approach:

1. **Report received**: Security team acknowledges the report
2. **Verification**: We verify and assess the vulnerability
3. **Fix development**: We develop and test a fix
4. **Release**: We release a security patch
5. **Public disclosure**: After the patch is released, we publish details

### Timeline

- **T+0**: Vulnerability reported
- **T+2 days**: Acknowledgment sent
- **T+7 days**: Assessment completed
- **T+30 days**: Fix released (for critical issues)
- **T+45 days**: Public disclosure

## Security Updates

Security updates are announced via:

- GitHub Security Advisories: <https://github.com/UlloaSP/mlschema/security/advisories>
- Release notes: <https://github.com/UlloaSP/mlschema/releases>
- Changelog: [docs/changelog.md](docs/changelog.md)

## Dependency Security

MLSchema depends on:

### Runtime Dependencies

- **pandas** (>=2.3.0): Well-maintained, security advisories tracked
- **Pydantic** (>=2.11.4): Strong security record, actively maintained

### Monitoring

We monitor security advisories for all dependencies using:

- GitHub Dependabot alerts
- PyPI security notifications
- Direct monitoring of upstream projects

### Updating Dependencies

We aim to:

- Update dependencies within 7 days of security releases
- Test updates thoroughly before releasing
- Maintain compatibility with supported Python versions

## Secure Development Practices

Our development process includes:

- **Code Review**: All changes reviewed before merging
- **Automated Testing**: Comprehensive test suite (279 tests, 80%+ coverage)
- **Static Analysis**: Pyright for type checking, Ruff for linting
- **Pre-commit Hooks**: Automated checks before commits
- **Continuous Integration**: Tests run on all PRs

## Security Checklist for Contributors

When contributing code:

- [ ] Input validation for all public APIs
- [ ] No arbitrary code execution
- [ ] No file system access (unless explicitly required)
- [ ] No network requests
- [ ] Type hints for all functions
- [ ] Tests covering edge cases
- [ ] Documentation of security considerations

## Security-Related Configuration

MLSchema has minimal configuration. Security-relevant settings:

```python
# Example: Safe usage pattern
from mlschema import MLSchema
from mlschema.strategies import NumberStrategy, TextStrategy

# Explicit strategy registration (opt-in security model)
mls = MLSchema()
mls.register(NumberStrategy())
mls.register(TextStrategy())

# Only registered strategies are used
schema = mls.build(dataframe)
```

## Contact

For security concerns:

- **Email**: <pablo.ulloa.santin@udc.es>
- **Subject**: `[SECURITY] MLSchema Vulnerability Report`

For general questions:

- **Issues**: <https://github.com/UlloaSP/mlschema/issues>
- **Discussions**: <https://github.com/UlloaSP/mlschema/discussions>

## Attribution

We appreciate responsible security researchers who help keep MLSchema safe. With your permission, we will:

- Credit you in the security advisory
- Add your name to our hall of fame (if you wish)
- Provide a reference for your responsible disclosure

Thank you for helping keep MLSchema and its users safe! 🔒

---

**Last Updated**: October 8, 2025
