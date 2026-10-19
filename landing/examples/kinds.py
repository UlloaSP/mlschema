import pandas as pd

from mlschema import infer_schema

df = pd.DataFrame(
    {
        "customer": ["Ada", "Linus", "Grace"],
        "age": [42, 55, 38],
        "tier": pd.Categorical(["pro", "free", "pro"], categories=["free", "pro"]),
        "plan__monthly": [1, 0, 0],
        "plan__yearly": [0, 1, 1],
        "active": [True, False, True],
        "created": pd.date_range("2024-01-01", periods=3),
        "readings": [
            (pd.Timestamp("2024-01-01"), 23.5),
            (pd.Timestamp("2024-01-02"), 24.1),
            (pd.Timestamp("2024-01-03"), 22.8),
        ],
    }
)

schema = infer_schema(df)
