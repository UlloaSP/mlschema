<p align="center">
  <img src="https://raw.githubusercontent.com/UlloaSP/mlschema/main/brand/mlschema.png" alt="" height="112" />
</p>

<h1 align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/UlloaSP/mlschema/main/brand/wordmark-dark.svg" />
    <img src="https://raw.githubusercontent.com/UlloaSP/mlschema/main/brand/wordmark-light.svg" alt="MLschema" height="52" />
  </picture>
</h1>

<p align="center">From pandas DataFrames to validated field schemas.</p>

<p align="center">
  <a href="https://mlschema.eshkra.dev/"><img src="https://img.shields.io/badge/website-303039?style=flat&amp;logo=astro&amp;logoColor=ff6a1a" alt="Website" /></a>
  <a href="https://docs.mlschema.eshkra.dev/"><img src="https://img.shields.io/badge/docs-303039?style=flat&amp;logo=readthedocs&amp;logoColor=ff6a1a" alt="Documentation" /></a>
  <a href="https://playground.mlschema.eshkra.dev/"><img src="https://img.shields.io/badge/playground-303039?style=flat&amp;logo=python&amp;logoColor=ff6a1a" alt="Playground" /></a>
  <a href="https://pypi.org/project/mlschema/"><img src="https://img.shields.io/pypi/v/mlschema?style=flat&amp;logo=pypi&amp;logoColor=white&amp;labelColor=303039&amp;color=b73d00" alt="PyPI version" /></a>
  <a href="https://github.com/UlloaSP/mlschema"><img src="https://img.shields.io/badge/source-303039?style=flat&amp;logo=github&amp;logoColor=white" alt="Source on GitHub" /></a>
  <a href="https://github.com/UlloaSP/mlschema/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/UlloaSP/mlschema/ci.yml?branch=main&amp;style=flat&amp;label=CI&amp;labelColor=303039" alt="CI status" /></a>
  <a href="https://github.com/UlloaSP/mlschema/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-b73d00?style=flat&amp;labelColor=303039" alt="MIT license" /></a>
  <a href="https://eshkra.dev"><img src="https://img.shields.io/badge/part_of-eshkra-b73d00?style=flat&amp;labelColor=303039" alt="Part of eshkra" /></a>
</p>

MLschema is a Python library for deriving validated field schemas from pandas DataFrames. It reads column names, dtypes, categories and nullability, then validates the inferred fields with Pydantic and returns a JSON-compatible list.

Use the result with [MLform](https://mlform.eshkra.dev/), include it in [MLbundle](https://github.com/UlloaSP/mlbundle), or consume it in your own frontend. Start with built-in inference, refine individual fields, or add domain-specific builders and kinds.

## Why infer a field schema?

The data pipeline already knows whether an input is a number, a date or a category. Writing those definitions again in a frontend creates another place for the model and its inputs to drift apart.

MLschema turns that information into a starting contract with explicit backend mappings. Your application supplies product-specific labels, bounds and defaults; the same validation path checks both inferred and customized fields. Inference runs locally and the resulting list is ordinary data, independent of a rendering framework.

## Installation

> MLschema is pre-1.0. Public contracts may change between minor releases. Requires Python 3.14 (`>=3.14,<3.15`); supported pandas 3 and Pydantic 2 versions are installed as dependencies.

```bash
uv add mlschema
```

Or install from PyPI with `pip install mlschema`.

See the [release and upgrade notes](https://docs.mlschema.eshkra.dev/changelog/) when updating an existing integration. Version 0.3 changes the series field contract.

## Quick start

Create a DataFrame with the dtypes your inputs should use:

```python
import json

import pandas as pd
from mlschema import infer_schema

frame = pd.DataFrame(
    {
        "age": [28, 41],
        "plan": pd.Categorical(["free", "pro"]),
        "active": [True, False],
    }
)

fields = infer_schema(frame)
print(json.dumps(fields, indent=2))
```

The result is a field list, ready to serialize:

```json
[
  {"kind": "number", "label": "age", "required": true, "mappedTo": "age", "step": 1.0},
  {"kind": "category", "label": "plan", "required": true, "mappedTo": "plan", "options": ["free", "pro"]},
  {"kind": "boolean", "label": "active", "required": true, "mappedTo": "active"}
]
```

Pass it to MLform as the schema's `fields` property. Your application owns reports, transport and model execution.

## Choose your customization

| API | Use it to |
| --- | --- |
| `infer_schema(frame)` | Infer fields using the built-in kinds. |
| `overrides={...}` | Refine a column's label, bounds or other supported properties before validation. |
| `builders=[...]` | Supply inference logic for an existing kind, before the built-in builders. |
| `kinds=[kind(model=..., infer=...)]` | Add a strict field model and the builder that produces it. |
| `with_positional_mappings(fields, feature_names)` | Copy a field list and convert mappings into an explicit model input order. |

For example, refine a label and bounds, then adapt the mappings for a model that consumes a feature vector:

```python
from mlschema import with_positional_mappings

fields = infer_schema(
    frame,
    overrides={"age": {"label": "Age", "min": 0, "max": 120}},
)
positional = with_positional_mappings(fields, ["plan", "age", "active"])
```

The `age` field keeps its displayed label `Age`; its target changes from `"age"` to position `1` in the returned copy. The helper rewrites mappings, preserving field order, series columns and one-hot grouping. It leaves the original list unchanged.

All application-facing functions and extension types come from `mlschema`. Public inference exceptions come from `mlschema.core`; see the [Python API](https://docs.mlschema.eshkra.dev/reference/api/).

## What is included?

- Inference for text, numbers, categories, booleans, dates and two-axis series.
- One-hot groups from named binary columns such as `color__red` and `color__blue`.
- Explicit backend mappings: names for named columns, positions for positional columns.
- Series output with ordered `columns[]`, compatible with MLform.
- Strict field validation, overrides, custom builders and custom kinds.
- A typed, function-first API that runs entirely in your Python process.

DataFrame dtypes matter: categorical options come from `category`, and date inference accepts specific datetime dtypes. Columns unclaimed by earlier builders reach the text fallback. See the [field-kind reference](https://docs.mlschema.eshkra.dev/schema/field-kinds/) for supported inputs and limits.

## Some notes

MLschema owns field inference, validation and explicit mappings. Your application owns rendering, report definitions, model training and execution. The output is a field list, not a JSON Schema document or a complete MLform schema.

Empty DataFrames are rejected, and invalid builder output or overrides fail validation. Inference does not establish that a dataset is suitable for a model. The returned list can contain category values, so treat it as part of your data contract when sharing it.

## Documentation

Full documentation lives at [docs.mlschema.eshkra.dev](https://docs.mlschema.eshkra.dev/).

- [Installation](https://docs.mlschema.eshkra.dev/getting-started/installation/)
- [Quick start](https://docs.mlschema.eshkra.dev/getting-started/quick-start/)
- [Field contract](https://docs.mlschema.eshkra.dev/schema/overview/)
- [Backend mappings](https://docs.mlschema.eshkra.dev/schema/mappings/)
- [Custom builders and kinds](https://docs.mlschema.eshkra.dev/guides/extensions/)
- [Python API](https://docs.mlschema.eshkra.dev/reference/api/)

Try the examples in the [Python playground](https://playground.mlschema.eshkra.dev/). It runs the repository's Python code in an experimental browser environment; its dependency limits are documented in the [playground guide](https://github.com/UlloaSP/mlschema/blob/main/playground/README.md).

## Contributing

Python development uses [uv](https://docs.astral.sh/uv/), Ruff, Pyright and pytest:

```bash
uv sync --locked --group dev
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
uv build
```

The landing page, documentation and playground use [Vite+](https://viteplus.dev/guide/) (`vp`) with a pnpm workspace. This tooling is separate from the Python package:

```bash
vp install --frozen-lockfile
vp run build
```

Read [CONTRIBUTING.md](https://github.com/UlloaSP/mlschema/blob/main/CONTRIBUTING.md) for local development and release setup.

Run `vp run dev:playground` to serve the local Python playground at `http://127.0.0.1:10011`. The [playground guide](https://github.com/UlloaSP/mlschema/blob/main/playground/README.md) covers examples and verification commands.

## License

MIT
