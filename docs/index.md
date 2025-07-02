# MLSchema

Welcome to the official documentation of **MLSchema**, a Python micro-library designed to infer and serialize input schemas automatically from a **pandas.DataFrame**, streamlining your data pipeline setup.

---

## 🚀 Quick Installation

```bash
uv add mlschema
```

See detailed installation instructions in the [Installation](installation.md) section.

## ⚡ Minimal Example

Here’s how you can quickly start using MLSchema:

```python
import pandas as pd
from mlschema.core import FieldService
from mlschema.strategies import TextStrategy

# Load your data
df = pd.read_csv("data.csv")

# Initialize the service and register strategies
service = FieldService()
service.register(TextStrategy())

# Automatically build schema from DataFrame
schema = service.build_schema_from_dataframe(df)
```

## 📌 Key Modules

| Module                | Purpose                                                             |
| --------------------- | ------------------------------------------------------------------- |
| `mlschema.core`       | Generic strategies, registry, and high-level service classes.       |
| `mlschema.strategies` | Concrete implementations for various field types and domain models. |

For full API details, see the [API Reference](reference.md).
