# MLSchema

> *Automated schema inference for data‑driven organisations, grn proven design, built for tomorrow.*

---

## 1. Executive Summary

**MLSchema** is a Python micro‑library that converts **pandas** dataframes into fully‑validated, front‑end‑ready JSON schemas. The goal: eliminate hand‑rolled form definitions, accelerate prototype‑to‑production cycles, and enforce data‑contract governance across your analytics stack.

| Metric                  | Outcome                                                                  |
| ----------------------- | ------------------------------------------------------------------------ |
| **Time‑to‑schema**      | < 150 ms on 10 k columns / 1 M rows (benchmarked on x86‑64, Python 3.14) |
| **Boilerplate reduced** | ≈ 90 % fewer lines of bespoke form code                                  |
| **Extensibility**       | Plug‑in architecture, register or swap strategies at runtime             |

---

## 2. Quick Installation

For green‑field projects or CI pipelines, a single command sets up MLSchema and its dependency graph using **[uv](https://docs.astral.sh/uv/)**:

```bash
uv add mlschema
```

For other package managers, refer to the dedicated [Installation](docs/installation.md) guide.

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

* **[Detailed Installation](docs/installation.md)**
* **[Usage Guide](docs/usage.md)**
* **[API Reference](docs/reference.md)**
* **[Changelog](CHANGELOG.md)**
* **[GitHub](https://github.com/UlloaSP/mlschema)**

> *Tradition meets innovation: MLSchema codifies time‑honoured form‑generation workflows while embracing Python's latest language features.*

---

## 7. Contributing

We welcome contributions! MLSchema is an open-source project that thrives on community input.

### How to Contribute

1. **Read the guidelines**: See [CONTRIBUTING.md](CONTRIBUTING.md)
2. **Pick an issue**: Check [Good First Issues](https://github.com/UlloaSP/mlschema/labels/good%20first%20issue)
3. **Submit a PR**: Follow our pull request template
4. **Join discussions**: Participate in [GitHub Discussions](https://github.com/UlloaSP/mlschema/discussions)

### Development Setup

```bash
# Clone the repository
git clone https://github.com/UlloaSP/mlschema.git
cd mlschema

# Install dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install

# Run tests
uv run pytest
```

For detailed development instructions, see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 8. License

MLSchema is released under the **MIT License**. See [LICENSE](LICENSE) for the full text.

### Third-Party Licenses

MLSchema depends on:

* **pandas** (BSD 3-Clause)
* **Pydantic** (MIT)

For complete license information of all dependencies, see [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).

---

## 9. Security

We take security seriously. If you discover a security vulnerability:

* **Do NOT** open a public issue
* **Email us** at: <pablo.ulloa.santin@udc.es>
* Include details following our [Security Policy](SECURITY.md)

See [SECURITY.md](SECURITY.md) for our complete security policy and disclosure process.

---

## 10. Citation

If you use MLSchema in your research or project, please cite:

```bibtex
@software{mlschema2025,
  author = {Ulloa Santín, Pablo},
  title = {MLSchema: Automated Schema Inference for pandas DataFrames},
  year = {2025},
  url = {https://github.com/UlloaSP/mlschema},
  version = {0.1.1}
}
```

---

## 11. Acknowledgments

MLSchema is built on top of excellent open-source projects:

* **pandas**: The foundational data analysis library
* **Pydantic**: Data validation using Python type annotations

See [AUTHORS.md](AUTHORS.md) for contributor recognition and [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) for full attribution.

---

## 12. Support

* **📖 Documentation**: [https://ulloasp.github.io/mlschema/](https://ulloasp.github.io/mlschema/)
* **🐛 Bug Reports**: [GitHub Issues](https://github.com/UlloaSP/mlschema/issues)
* **💬 Discussions**: [GitHub Discussions](https://github.com/UlloaSP/mlschema/discussions)
* **📧 Contact**: <pablo.ulloa.santin@udc.es>

---

**Made with ❤️ by [Pablo Ulloa Santín](https://github.com/UlloaSP)**
