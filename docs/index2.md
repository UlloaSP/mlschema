# MLSchema

> *Lightweight SDK for turning **pandas** dataframes into front-end-ready JSON schemas—designed to integrate seamlessly with the [mlform](https://github.com/UlloaSP/mlform) web component, yet fully usable on its own.*

---

## 1 · Executive Summary

**MLSchema** converts tabular data into validated JSON field definitions, eliminating hand-coded forms and accelerating delivery of data-driven UIs.
Built for side-projects but crafted with enterprise design discipline, it follows a strategy pattern that keeps the core lean while allowing domain-specific extensions.

| Value Driver            | Detail                                                          |
|-------------------------|-----------------------------------------------------------------|
| **Contract enforcement**| Pydantic v2 validation guarantees column–to–field fidelity.     |
| **Plug-and-play**       | Works stand-alone *or* as the schema engine for **mlform**.     |
| **Extensible**          | Register or swap strategies at runtime—no consumer refactor.    |
| **Zero friction**       | Sensible defaults; no configuration required for common dtypes. |

---

## 2 · Installation

| Environment  | Command                           | Notes                                |
|--------------|-----------------------------------|--------------------------------------|
| **Modern**   | `uv add mlschema`                 | Fast resolver, deterministic lockfile|
| **Legacy**   | `pip install mlschema`            | Python ≥ 3.9, pandas ≥ 2.0           |

> MLSchema ships with no optional binaries and has no hard C-extensions, making installation predictable across CI/CD, Docker and workstation setups.

---

## 3 · 60-Second Quick-Start

```python
import pandas as pd
from mlschema import MLSchema

# 1 · Load data
df = pd.read_csv("customers.csv")

# 2 · Infer schema using built-in strategies
schema = MLSchema().build(df)

# 3 · Send to the front end
print(schema.model_dump_json(indent=2))
```

Pair the resulting JSON with **mlform** to render an HTML form instantly.

---

## 4 · Architecture at a Glance

| Component           | Responsibility                                  | Extension Hook               |
|---------------------|-------------------------------------------------|------------------------------|
| `mlschema.MLSchema` | Strategy registry, validation, JSON emission    | `register()`, `unregister()` |
| Built-in *Strategies* | Map pandas dtypes → field controls            | Subclass `Strategy`          |
| `BaseField` (Pydantic) | Canonical field blueprint                     | Custom Pydantic models       |

### Why Strategies?

* **Single-responsibility** – each strategy owns exactly one column type.
* **Hot-swap** – override behaviour without touching consumer code.
* **Future-proof** – drop-in geospatial, IoT or custom widgets as needed.

---

## 5 · Key Features

1. **Automatic schema inference** – text, numeric, categorical, boolean and date handled out of the box.
2. **Pydantic v2 validators** – schema is fully typed and runtime-safe.
3. **No external services** – all processing is in-process; suitable for air-gapped environments.
4. **Typed returns** – JSON schema is delivered as a Pydantic model for IDE autocompletion.

---

## 6 · Compatibility Matrix

| Dependency | Minimum Version | Tested On |
|------------|-----------------|-----------|
| Python     | 3.9             | 3.9 – 3.14|
| pandas     | 2.0             | 2.0 – 2.2 |
| pydantic   | 2.4             | 2.4 – 2.7 |

---

## 7 · Roadmap (Community-Driven)

| Quarter | Milestone                               |
|---------|-----------------------------------------|
| Q4 2025 | Add **TimeSeriesStrategy**              |
| Q1 2026 | CLI helper: `mlschema infer data.csv`   |
| Q2 2026 | Publish VS Code snippets & templates    |

Have an idea? [Open an issue](https://github.com/UlloaSP/mlschema/issues).

---

## 8 · Further Reading

* **[Usage Guide](usage.md)** – deeper walkthrough with custom strategies.
* **[Detailed Installation](installation.md)** -
* **[API Reference](reference.md)** – full docstrings and type hints.
* **[mlform](https://github.com/UlloaSP/mlform)** – sibling library that renders the schemas.

> *Respecting proven patterns, built for tomorrow’s stack.*
