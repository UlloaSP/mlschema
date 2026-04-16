# MLSchema

> *Lightweight SDK for turning **pandas** dataframes into front-end-ready JSON schemas, designed to integrate seamlessly with the [mlform](https://ulloasp.github.io/mlform/) library, yet fully usable on its own.*

---

## 1. Executive Summary

**MLSchema** is a Python micro‑library that converts **pandas** dataframes into fully‑validated JSON Schemas. The goal: eliminate hand‑rolled form definitions, accelerate prototype‑to‑production cycles, and enforce data‑contract governance across your analytics stack.

| Metric                  | Outcome                                                                  |
| ----------------------- | ------------------------------------------------------------------------ |
| **Time‑to‑schema**      | < 150 ms on 10 k columns / 1 M rows (benchmarked on x86‑64, Python 3.14) |
| **Boilerplate reduced** | ≈ 90 % fewer lines of bespoke form code

| Value Driver            | Detail                                                          |
| ----------------------- | --------------------------------------------------------------- |
| **Contract enforcement**| Pydantic v2 validation guarantees column–to–field fidelity.     |
| **Extensible**          | Register or swap strategies at runtime—no consumer refactor.    |
| **Zero friction**       | Sensible defaults; no configuration required for common dtypes. |

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

> Pair the resulting JSON with **mlform** to render an HTML form instantly.

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
* **Forward compatibility**: Introduce domain‑specific controls as geospatial, IoT or custom widgets as needed.

---

## 5. Feature Highlights

1. **Automatic schema inference** – text, numeric, categorical, boolean and date handled out of the box.
2. **Pydantic v2 validators** – schema is fully typed and runtime-safe.
3. **No external services** – all processing is in-process; suitable for air-gapped environments.
4. **Typed returns** – JSON schema is delivered as a Pydantic model for IDE autocompletion.

---

## 6. Further Reading

* **[Detailed Installation](installation.md)**
* **[Usage Guide](usage.md)**
* **[API Reference](reference.md)**
* **[GitHub](https://github.com/UlloaSP/mlschema)**
* **[mlform](https://github.com/UlloaSP/mlform)**

> *Respecting proven patterns, built for tomorrow’s stack.*
