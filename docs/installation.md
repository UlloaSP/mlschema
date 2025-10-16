# Installation

This section provides a *battle‑tested* playbook for deploying **mlschema** in isolated, reproducible environments. Follow the steps below to guarantee a friction‑free rollout on any CI pipeline or local workstation.

---

## 1. Supported Runtimes

| Runtime               | Version                                             |
| --------------------- | --------------------------------------------------- |
| **Python**            | `>= 3.14`                                           |
| **Operating Systems** | Windows 11                                          |

---

## 2. One‑Line Installation (Recommended)

`mlschema` is published on **PyPI**. The project team endorses **[uv](https://docs.astral.sh/uv/)** for its deterministic dependency graph and automatic virtual‑environment management:

```bash
uv add mlschema
```

### Alternative Package Managers

| Package Manager | Command                                 |
| --------------- | --------------------------------------- |
| **pip**         | `pip install mlschema`                  |
| **poetry**      | `poetry add mlschema`                   |
| **conda**       | `conda install -c conda-forge mlschema` |
| **pipenv**      | `pipenv install mlschema`               |

> **Tip**
> Pin a specific version (`mlschema==x.y.z`) if your governance model mandates lock‑step dependencies.

---

## 3. Post‑Install Verification

Run the following smoke tests to confirm a healthy installation:

```bash
# List the resolved dependency tree (uv only)
uv tree

# Validate import & print version
python - << 'PY'
import mlschema
print("mlschema version:", mlschema.__version__)
PY
```

A successful import indicates that C‑extensions (if any) and pure‑Python wheels have been correctly resolved.

---

## 4. Runtime Dependencies

All transitive dependencies are resolved automatically by your package manager. For audit purposes, the bill of materials is:

| Package      | Minimal Version |
| ------------ | --------------- |
| **pydantic** | `>= 2.11.4`     |
| **pandas**   | `>= 2.3.0`      |
| **numpy**    | `>= 2.3.0`      |

> **Notice**
> `mlschema` leverages Python 3.14’s **zero‑cost structural pattern matching** and **buffer protocol optimisations**—downgrades are not supported.

---

## 5. Virtual‑Environment Workflow (Best Practice)

### Using uv (zero‑configuration)

```bash
uv venv           # creates .venv and activates it
uv add mlschema    # installs package + deps
```

### Manual venv (fallback)

```bash
# macOS/Linux
python -m venv .venv
source .venv/bin/activate
pip install mlschema
```

```powershell
# Windows PowerShell
.\.venv\Scripts\activate
pip install mlschema
```

> **Why isolate?**
> Prevents dependency drift and shields global Python installs from conflicting package versions.

---

## 6. Version & Status Badges

![PyPI version](https://badge.fury.io/py/mlschema.svg)
[![CI](https://github.com/UlloaSP/mlschema/actions/workflows/ci.yml/badge.svg)](https://github.com/UlloaSP/mlschema/actions/workflows/ci.yml)

---

## 7. Troubleshooting & Known Issues

| Symptom                                       | Root Cause                             | Resolution                                             |
| --------------------------------------------- | -------------------------------------- | ------------------------------------------------------ |

*No open CVEs or platform‑specific incompatibilities have been reported as of July 2025.*

---

## 8. Further Reading

* **[Usage Guide](usage.md)**
* **[API Reference](reference.md)**
* **[GitHub](https://github.com/UlloaSP/mlschema)**
* **[Contributing](https://github.com/UlloaSP/mlschema/blob/main/CONTRIBUTING.md)**
