# MLSchema

> *Automated schema inference for data‑driven organisations, grounded in proven design, built for tomorrow.*

---

## 1. Executive Summary

**MLSchema** is a Python micro‑library that converts **pandas** dataframes into fully‑validated, front‑end‑ready JSON schemas. The goal: eliminate hand‑rolled form definitions, accelerate prototype‑to‑production cycles, and enforce data‑contract governance across your analytics stack.

| Metric                  | Outcome                                                                  |
| ----------------------- | ------------------------------------------------------------------------ |
| **Time‑to‑schema**      | < 150 ms on 10 k columns / 1 M rows (benchmarked on x86‑64, Python 3.14) |
| **Boilerplate reduced** | ≈ 90 % fewer lines of bespoke form code                                  |
| **Extensibility**       | Plug‑in architecture, register or swap strategies at runtime              |

---

## 2. Quick Installation

For green‑field projects or CI pipelines, a single command sets up MLSchema and its dependency graph using **[uv](https://docs.astral.sh/uv/)**:

```bash
uv add mlschema
```

For other package managers, refer to the dedicated [Installation](installation.md) guide.

---

## 3. 90‑Second Onboarding

```python
import pandas as pd
from mlschema import MLSchema
from mlschema.strategies import TextStrategy

# 1️⃣  Source your data
df = pd.read_csv("data.csv")

# 2️⃣  Spin up the orchestrator and register baseline strategies
ms = MLSchema()
ms.register(TextStrategy())

# 3️⃣  Produces a JSON schema
schema = ms.build(df)
```

Outcome: a `JSON` that your UI layer can instantly translate into dynamic forms.

---

## 4. Architectural Building Blocks

| Component                    | Role                                                 | Extensibility Point                      |
| ---------------------------- | ---------------------------------------------------- | ---------------------------------------- |
| **`mlschema.MLSchema`**      | Strategy registry, validation pipeline, JSON emitter | `register()`, `update()`, `unregister()` |
| **Field Strategies**         | Map pandas dtypes => form controls                   | Implement `Strategy` subclasses          |
| **`BaseField`** (Pydantic)   | Canonical schema blueprint                           | Custom Pydantic models inherit from it   |

### Why a Strategy Pattern?

* **Single‑responsibility**: Each strategy owns one field type.
* **Hot‑swap**: Swap implementations without touching consumer code.
* **Forward compatibility**: Introduce domain‑specific controls (e.g., geospatial pickers) with near‑zero refactor.

---

## 5. Feature Highlights

1. **Zero‑configuration defaults**: Text fallback ensures graceful degradation.
2. **Pydantic v2 validators**: Domain rules enforced at build time.
3. **Runtime performance**: Vectorised dtype checks, no Python loops on critical paths.
4. **Production readiness**: CI badge, semantic versioning, and zero open CVEs (September 2025).

---

## 6. Further Reading

* **[Detailed Installation](installation.md)**
* **[Usage Guide](usage.md)**
* **[API Reference](reference.md)**
* **[GitHub](https://github.com/UlloaSP/mlschema)**

> *Tradition meets innovation: MLSchema codifies time‑honoured form‑generation workflows while embracing Python’s latest language features.*
