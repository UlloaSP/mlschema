import pandas as pd

from mlschema import infer_schema

df = pd.DataFrame(
    {
        "tier": pd.Categorical(["pro", "free", "pro"], categories=["free", "pro"]),
        # 0/1 columns sharing a "feature__value" prefix become one field whose
        # options keep their own mappedTo targets.
        "color__red": [1, 0, 0],
        "color__green": [0, 1, 0],
        "color__blue": [0, 0, 1],
    }
)

infer_schema(df)
