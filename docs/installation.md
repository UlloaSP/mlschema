# 📦 Installation

`mlschema` is available as a Python package on [PyPI](https://pypi.org/). You can install it with your preferred package manager. We recommend **[uv](https://docs.astral.sh/uv/)** because it streamlines dependency management and automatically isolates virtual environments, ensuring a clean setup.

| Package Manager                                   | Command                                 |
| ----------------------------------------          | --------------------------------------- |
| [**uv**](https://docs.astral.sh/uv/)              | `uv add mlschema`                       |
| [**pip**](https://pypi.org/project/pip/)          | `pip install mlschema`                  |
| [**poetry**](https://python-poetry.org/)          | `poetry add mlschema`                   |
| [**conda**](https://anaconda.org/anaconda/conda)  | `conda install -c conda-forge mlschema` |
| [**pipenv**](https://pypi.org/project/pipenv/)    | `pipenv install mlschema`               |

## ✅ Quick Verification

After installation, verify that `mlschema` works as expected:

```bash
# Display dependency tree and verify uv environment
uv tree

# Verify import and version
python -c "import mlschema; print('mlschema version:', mlschema.__version__)"
```

## ⚙️ Requirements

* **Python version**: `>=3.13`
* **Dependencies** (installed automatically):

  * [pydantic](https://pydantic.dev/) `>=2.11.4`
  * [pandas](https://pandas.pydata.org/) `>=2.3.0`
  * [numpy](https://numpy.org/) `>=2.3.0`

> **Note:** `mlschema` has been tested on Windows. For large datasets, ensure you have enough RAM and sufficient disk space.

## 🛠️ Virtual Environments (Recommended)

It is highly recommended to install `mlschema` in a virtual environment:

```bash
# Using uv
uv venv
uv add mlschema
```

```bash
# Manual venv alternative
python -m venv .venv
pip install mlschema
```

```bash
# macOS/Linux
source .venv/bin/activate
pip install mlschema
```

```powershell
# Windows PowerShell
.\venv\Scripts\activate
pip install mlschema
```

## 🔖 Version Badge

![PyPI version](https://badge.fury.io/py/mlschema.svg)

## 📖 More Information

* [Official MLSchema Documentation](usage.md)
* [MLSchema GitHub Repository](https://github.com/UlloaSP/mlschema)
* [Contribution Guidelines](https://github.com/UlloaSP/mlschema/blob/main/CONTRIBUTING.md)

⚠️ **Known Issues:**
There are no known incompatibilities at this time. Please [report any issues](https://github.com/UlloaSP/mlschema/issues).
