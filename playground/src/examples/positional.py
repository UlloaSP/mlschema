import pandas as pd

from mlschema import infer_schema, with_positional_mappings

df = pd.DataFrame(
    {
        "age": [36, 54],
        "smoker": [True, False],
        "plan__basic": [1, 0],
        "plan__premium": [0, 1],
    }
)
schema = infer_schema(df)

# A model trained on a NumPy matrix expects inputs by position, not by name.
feature_names = ["plan__basic", "plan__premium", "age", "smoker"]

with_positional_mappings(schema, feature_names)
