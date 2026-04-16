# MLSchema

[![PyPI - Version](https://img.shields.io/pypi/v/mlschema.svg)](https://pypi.org/project/mlschema/)
[![Python Versions](https://img.shields.io/pypi/pyversions/mlschema.svg)](https://pypi.org/project/mlschema/)
[![CI](https://github.com/UlloaSP/mlschema/actions/workflows/ci.yml/badge.svg)](https://github.com/UlloaSP/mlschema/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/UlloaSP/mlschema.svg)](https://github.com/UlloaSP/mlschema/blob/main/LICENSE)

> Lightweight orchestration layer that turns pandas DataFrames into front-end-ready JSON schemas, engineered to pair seamlessly with [mlform](https://github.com/UlloaSP/mlform).

## Contents

- [MLSchema](#mlschema)
  - [Contents](#contents)
  - [Overview](#overview)
  - [Key Features](#key-features)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Quick Start](#quick-start)
  - [Schema Output](#schema-output)
  - [How It Works](#how-it-works)
  - [Built-in Strategies](#built-in-strategies)
  - [Extending MLSchema](#extending-mlschema)
  - [Validation \& Error Handling](#validation--error-handling)
  - [Tooling \& Quality](#tooling--quality)
  - [Resources](#resources)
  - [Contributing](#contributing)
  - [Security](#security)
  - [License](#license)

## Overview

`mlschema` accelerates form and contract generation by automatically deriving JSON field definitions from tabular data. The library applies a strategy-driven pipeline on top of pandas, validating every payload with Pydantic before it reaches your UI tier or downstream services.

- Converts analytics data into stable JSON schemas in a few lines of code.
- Keeps inference logic server-side; no external services or background workers required.
- Ships with production-tested strategies for text, numeric, categorical, boolean, and temporal data.
- Designed for synchronous use alongside [mlform](https://ulloasp.github.io/mlform/), yet fully usable on its own.

## Key Features

- Strategy registry that lets you opt into only the field types you want to expose.
- Pydantic v2 models guarantee structural validity and embed domain-specific constraints.
- Normalized dtype matching covers both pandas extension types and NumPy dtypes.
- Deterministic JSON output (`inputs` / `outputs`) suitable for form engines and low-code tooling.
- Fully typed public API with strict static analysis (Pyright) and comprehensive tests.

## Requirements

- Python `>= 3.14, < 3.15`
- pandas `>= 2.3.3, < 3.0.0`
- pydantic `>= 2.12.3, < 3.0.0`

All transitive dependencies are resolved automatically by your package manager.

## Installation

```bash
uv add mlschema
```

Alternative package managers:

- `pip install mlschema`
- `poetry add mlschema`
- `conda install -c conda-forge mlschema`
- `pipenv install mlschema`

Pin a version (for example `mlschema==0.1.2`) when you need deterministic environments.

## Quick Start

```python
import pandas as pd
from mlschema import MLSchema
from mlschema.strategies import TextStrategy, NumberStrategy, CategoryStrategy

df = pd.DataFrame(
  {
    "name": ["Ada", "Linus", "Grace"],
    "score": [98.5, 86.0, 91.0],
    "role": pd.Categorical(["engineer", "engineer", "scientist"]),
  }
)

builder = MLSchema()
builder.register(TextStrategy())      # fallback for unsupported dtypes
builder.register(NumberStrategy())
builder.register(CategoryStrategy())

schema = builder.build(df)
```

## Schema Output

The payload is ready to serialise to JSON and inject into your UI or downstream service:

```json
{
  "inputs": [
  {"title": "name", "required": true, "type": "text"},
  {"title": "score", "required": true, "type": "number", "step": 0.1},
  {"title": "role", "required": true, "type": "category", "options": ["engineer", "scientist"]}
  ],
  "outputs": []
}
```

`TextStrategy` acts as the default fallback. Make sure it is registered when you want unsupported columns to degrade gracefully.

## How It Works

1. **Registry orchestration** – `MLSchema` keeps an in-memory registry of field strategies, keyed by a logical `type_name` and one or more pandas dtypes.
2. **Inference pipeline** – each DataFrame column is normalised, matched against the registry, and dispatched to the first compatible strategy.
3. **Schema materialisation** – strategies merge required metadata (title, type, required) with data-driven attributes, then dump the result through a Pydantic model.
4. **Structured output** – the service returns the canonical `{"inputs": [...], "outputs": []}` payload that feeds [mlform](https://ulloasp.github.io/mlform/) or any form rendering layer.

## Built-in Strategies

| Strategy class | `type` name | Supported pandas dtypes | Additional attributes |
| -------------- | ----------- | ----------------------- | --------------------- |
| `TextStrategy` | `text`      | `object`, `string`      | `minLength`, `maxLength`, `pattern`, `value`, `placeholder` |
| `NumberStrategy` | `number`  | `int64`, `int32`, `float64`, `float32` | `min`, `max`, `step`, `value`, `unit`, `placeholder` |
| `CategoryStrategy` | `category` | `category` | `options`, `value` |
| `BooleanStrategy` | `boolean` | `bool`, `boolean` | `value` |
| `DateStrategy` | `date` | `datetime64[ns]`, `datetime64` | `min`, `max`, `value`, `step` |

Register only the strategies you need. Duplicate registrations raise explicit errors; use `MLSchema.update()` to swap implementations at runtime.

## Extending MLSchema

Create bespoke field types by pairing a custom Pydantic model with a strategy implementation:

```python
from typing import Literal
from pandas import Series
from mlschema.core import BaseField, Strategy


class RatingField(BaseField):
  type: Literal["rating"] = "rating"
  min: int | None = None
  max: int | None = None
  precision: float = 0.5


class RatingStrategy(Strategy):
  def __init__(self) -> None:
    super().__init__(
      type_name="rating",
      schema_cls=RatingField,
      dtypes=("float64",),
    )

  def attributes_from_series(self, series: Series) -> dict:
    return {
      "min": float(series.min()),
      "max": float(series.max()),
    }
```

- Use `Strategy.dtypes` to advertise the pandas dtypes your strategy understands.
- Avoid mutating the incoming `Series`; treat it as read-only.
- Reserved keys (`title`, `type`, `required`, `description`) are populated by the base class.

Reference the full guide at [https://ulloasp.github.io/mlschema/usage/](https://ulloasp.github.io/mlschema/usage/) for end-to-end patterns.

## Validation & Error Handling

- `EmptyDataFrameError` – raised when the DataFrame has no rows or columns.
- `FallbackStrategyMissingError` – triggered if an unsupported dtype is encountered without a registered fallback.
- `StrategyNameAlreadyRegisteredError` / `StrategyDtypeAlreadyRegisteredError` – guard against duplicate registrations.
- Pydantic `ValidationError` / `PydanticCustomError` – surface invalid field constraints early (`min`/`max`, regex patterns, date ranges, etc.).

All exceptions derive from `mlschema.core.MLSchemaError`, making it straightforward to trap library-level failures.

## Tooling & Quality

- Distributed as an MIT-licensed wheel and sdist built with Hatchling.
- Strict typing (`pyright`) and linting (`ruff`) shipped with the repo.
- Test suite powered by `pytest` and `pytest-cov`; coverage reports live alongside the source tree.
- `py.typed` marker ensures type information propagates to downstream projects.

## Resources

- Documentation portal: [https://ulloasp.github.io/mlschema/](https://ulloasp.github.io/mlschema/)
- API reference: [https://ulloasp.github.io/mlschema/reference/](https://ulloasp.github.io/mlschema/reference/)
- Changelog: [https://ulloasp.github.io/mlschema/changelog/](https://ulloasp.github.io/mlschema/changelog/)
- Issue tracker: [https://github.com/UlloaSP/mlschema/issues](https://github.com/UlloaSP/mlschema/issues)
- Discussions: [https://github.com/UlloaSP/mlschema/discussions](https://github.com/UlloaSP/mlschema/discussions)
- mlform (optional form renderer): [https://github.com/UlloaSP/mlform](https://github.com/UlloaSP/mlform)

## Contributing

Community contributions are welcome. Review the guidelines and pick an issue to get started:

- Contribution guide: [https://github.com/UlloaSP/mlschema/blob/main/CONTRIBUTING.md](https://github.com/UlloaSP/mlschema/blob/main/CONTRIBUTING.md)
- Good first issues: [https://github.com/UlloaSP/mlschema/labels/good%20first%20issue](https://github.com/UlloaSP/mlschema/labels/good%20first%20issue)
- Development workflow: `uv sync`, `uv run pre-commit install`, `uv run pytest`

## Security

Please report security concerns privately by emailing `pablo.ulloa.santin@udc.es`. The coordinated disclosure process is documented at [https://github.com/UlloaSP/mlschema/blob/main/SECURITY.md](https://github.com/UlloaSP/mlschema/blob/main/SECURITY.md).

## License

Released under the MIT License. Complete terms and third-party attributions are available at:

- License: [https://github.com/UlloaSP/mlschema/blob/main/LICENSE](https://github.com/UlloaSP/mlschema/blob/main/LICENSE)
- Third-party notices: [https://github.com/UlloaSP/mlschema/blob/main/THIRD_PARTY_LICENSES.md](https://github.com/UlloaSP/mlschema/blob/main/THIRD_PARTY_LICENSES.md)

---

Made by [Pablo Ulloa Santin](https://github.com/UlloaSP) and the MLSchema community.
