import pandas as pd

from mlschema import infer_schema

# The features a house-price model was trained on.
df = pd.DataFrame(
    {
        "area_m2": [74.5, 120.0, 56.2],
        "rooms": [3, 5, 2],
        "district": pd.Categorical(["center", "north", "center"]),
        "has_lift": [True, False, True],
    }
)

schema = infer_schema(df)
