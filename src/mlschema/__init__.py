"""Production-grade orchestration for translating **pandas** DataFrames into
validated JSON field schemas.

The package exports a single façade—:class:`mlschema.MLSchema`
(alias :pydata:`mlform.MLForm`) which wraps the internal *Service/Registry*
subsystem.  Client code typically:

1. **Registers** concrete field strategies.
2. **Builds** a JSON-serialisable schema from a DataFrame.

Public surface:
    * `MLSchema`                 — canonical entry point
    * `mlschema.core.Strategy`   — extension contract (advanced)
    * `mlschema.core.BaseField`  — Pydantic base model (advanced)
    * All runtime errors derive from `mlschema.core.MLSchemaError`.

Example:
    ```python
    from mlschema import MLSchema
    from mlschema.strategies import NumberStrategy
    import pandas as pd

    ms = MLSchema()
    ms.register(NumberStrategy())

    df = pd.DataFrame({"age": [22, 37, 29]})
    schema = ms.build(df)
    ```
"""

from .mls import MLSchema

__version__ = "0.1.1"
__all__ = ["MLSchema"]
