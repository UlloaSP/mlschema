---
title: Installation
description: Install MLschema from PyPI, check the supported Python and dependency ranges, and verify the result.
---

```bash
uv add mlschema
```

MLschema is a pure-Python package on [PyPI](https://pypi.org/project/mlschema/). Any standard
installer works:

```bash
pip install mlschema
poetry add mlschema
```

Inside a Conda environment, activate it and use `pip`.

## Requirements

| Dependency | Supported range |
| --- | --- |
| Python | `>=3.14,<3.15` |
| pandas | `>=3.0.3,<4.0.0` |
| pydantic | `>=2.13.4,<3.0.0` |

pandas and pydantic are installed with the package. Install them explicitly only when your own code
imports them, which it usually does for pandas.

## Pin a version

Inference rules and the field contract can change between minor versions while MLschema is pre-1.0.
Pin the version you tested and upgrade deliberately after reading the [changelog](/changelog/):

```bash
uv add "mlschema==0.3.0"
pip install "mlschema==0.3.0"
```

## Verify the installation

```python
from importlib.metadata import version

import pandas as pd

from mlschema import infer_schema

print(version("mlschema"))
print(infer_schema(pd.DataFrame({"score": [98.5, 86.0]})))
```

The second line prints a list with one field:

```text
[{'label': 'score', 'required': True, 'mappedTo': 'score', 'kind': 'number', 'step': 0.1}]
```

## Troubleshooting

| Symptom | Likely cause | Resolution |
| --- | --- | --- |
| `No matching distribution found for mlschema` | Python is outside `>=3.14,<3.15`, or PyPI is unreachable. | Check `python --version` and your package index. |
| `ModuleNotFoundError: No module named 'mlschema'` | The package is in a different environment. | Activate the intended environment and reinstall. |
| Most fields come back as `text` | Columns are stored as `object`, `str`, or a nullable extension dtype. | Convert columns to the dtypes listed in [Field kinds](/schema/field-kinds/). |
| `EmptyDataFrameError` | The DataFrame has no rows or no columns. | Check the data before inference. |
| `pydantic.ValidationError` | An override, builder, or custom kind produced invalid constraints. | See [Errors](/guides/errors/). |

## Working on MLschema itself

The library uses [uv](https://docs.astral.sh/uv/), [Ruff](https://docs.astral.sh/ruff/), and
[Pyright](https://microsoft.github.io/pyright/):

```bash
uv sync
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
```

This documentation is an Astro Starlight project under `docs/`, using Vite+ (`vp`) and the
repository's pnpm workspace. Use Node.js 22.18+, 24.11+, or 26+:

```bash
vp install --frozen-lockfile
vp run docs#dev
vp run docs#build
```
