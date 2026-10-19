import pandas as pd

from mlschema import infer_schema

df = pd.DataFrame(
    {
        "name": ["Ada", "Linus", "Grace"],
        "age": [36, 54, 85],
        "score": [98.5, 86.0, None],
        "active": [True, False, True],
        "joined": pd.to_datetime(["2024-01-05", "2024-03-12", "2024-07-30"]),
    }
)

print(df.dtypes.to_string())

# The last expression is shown as JSON on the right.
infer_schema(df)
