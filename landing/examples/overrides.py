import pandas as pd

from mlschema import infer_schema

df = pd.DataFrame(
    {
        "age": [42, 55, 38],
        "tier": pd.Categorical(["pro", "free", "pro"], categories=["free", "pro"]),
    }
)

overrides = {
    "age": {
        "label": "Age",
        "description": "Customer age in years.",
        "min": 0,
        "max": 120,
        "unit": "years",
    },
    "tier": {"label": "Plan", "defaultValue": "pro"},
}

schema = infer_schema(df, overrides=overrides)
