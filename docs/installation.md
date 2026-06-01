# Installation

`mlschema` is distributed through PyPI and can be installed with any standard Python package manager.

The recommended setup is a project-local virtual environment with pinned dependencies. This keeps schema inference reproducible across local development, CI, notebooks, and backend services.

---

## Requirements

| Dependency | Version           |
| ---------- | ----------------- |
| Python     | `>=3.14,<3.15`    |
| pandas     | `>=3.0.3,<4.0.0`  |
| pydantic   | `>=2.13.4,<3.0.0` |

Runtime dependencies are resolved automatically by the package manager. In normal projects, only `mlschema` needs to be installed explicitly.

---

## Install With uv

For new or existing `uv` projects:

```bash
uv add mlschema
```

Pin a specific version when the environment must be reproducible:

```bash
uv add "mlschema==0.2.0"
```

`uv` updates the project dependency metadata and lockfile, so this is the preferred option for applications, libraries, and CI workflows that already use `uv`.

---

## Install With pip

For a standard virtual environment:

```bash
pip install mlschema
```

Pinned installation:

```bash
pip install "mlschema==0.2.0"
```

When working inside a Conda environment, use `pip` after activating the environment:

```bash
conda create -n mlschema-demo python=3.14
conda activate mlschema-demo
pip install mlschema
```

---

## Install With Poetry

```bash
poetry add mlschema
```

Pinned installation:

```bash
poetry add "mlschema==0.2.0"
```

---

## Virtual Environment Setup

A project-local virtual environment avoids dependency drift and prevents global Python packages from affecting schema generation.

Using `uv`:

```bash
uv venv
```

Activate the environment on macOS or Linux:

```bash
source .venv/bin/activate
```

Activate the environment on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Then install:

```bash
uv pip install mlschema
```

Using the standard library:

```bash
python -m venv .venv
```

macOS or Linux:

```bash
source .venv/bin/activate
pip install mlschema
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install mlschema
```

---

## Verify The Installation

A successful installation should import `mlschema`, expose `infer_schema()`, and generate a field list from a small DataFrame.

```bash
python - << 'PY'
from importlib.metadata import version

import pandas as pd

from mlschema import infer_schema

df = pd.DataFrame(
    {
        "name": ["Ada", "Linus"],
        "score": [98.5, 86.0],
        "active": [True, False],
    }
)

schema = infer_schema(df)

print("mlschema version:", version("mlschema"))
print(schema)
PY
```

Expected shape:

```python
[
    {"kind": "text", "label": "name", "required": True},
    {"kind": "number", "label": "score", "required": True, "step": 0.1},
    {"kind": "boolean", "label": "active", "required": True},
]
```

The exact formatting may differ depending on how the list is printed, but the important part is that the output is a direct field list.

---

## CI Installation

For CI pipelines using `uv`, install the project and run tests from the lockfile:

```bash
uv sync
uv run pytest
```

For simple package smoke checks:

```bash
uv venv
uv pip install mlschema
uv run python -c "from mlschema import infer_schema; print(infer_schema)"
```

For `pip`-based CI:

```bash
python -m pip install --upgrade pip
python -m pip install mlschema
python -c "from mlschema import infer_schema; print(infer_schema)"
```

---

## Troubleshooting

| Symptom                                           | Likely cause                                                                     | Resolution                                                                   |
| ------------------------------------------------- | -------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `No matching distribution found for mlschema`     | Python version is outside the supported range or package indexes are restricted. | Check `python --version` and confirm that PyPI access is available.          |
| `ModuleNotFoundError: No module named 'mlschema'` | The package was installed into a different environment.                          | Activate the intended virtual environment and reinstall.                     |
| `ImportError` involving pandas or pydantic        | Dependency resolution produced an incompatible environment.                      | Recreate the environment and install from a clean lockfile.                  |
| Schema output is mostly `text`                    | DataFrame columns are stored as ambiguous `object` values.                       | Convert columns to deliberate pandas dtypes before calling `infer_schema()`. |
| `EmptyDataFrameError`                             | The input DataFrame has no rows or no columns.                                   | Validate the DataFrame before schema inference.                              |
| Pydantic `ValidationError`                        | An override or custom kind emitted invalid field constraints.                    | Check bounds, defaults, options, and custom field models.                    |

---

## Versioning

`mlschema` follows semantic versioning.

Patch releases should be safe for compatible fixes. Minor releases may add supported field behaviour or public API surface. Breaking changes are documented in the [Changelog](changelog.md).

For production systems, pin a known version and upgrade deliberately:

```bash
uv add "mlschema==0.2.0"
```

---

## Next Steps

After installation, continue with the [Usage Guide](usage.md) to infer your first schema, apply overrides, and add custom builders or custom kinds.

For the exact field contract, see the [Schema Standard](schema-standard.md).

For public symbols and signatures, see the [API Reference](reference.md).
