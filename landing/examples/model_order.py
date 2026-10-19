import pandas as pd

from mlschema import infer_schema, with_positional_mappings

df = pd.DataFrame(
    {
        "age": [42, 55, 38],
        "plan__monthly": [1, 0, 0],
        "plan__yearly": [0, 1, 1],
    }
)

# The model reads one array, in the feature order it was trained with.
feature_names = ["plan__monthly", "plan__yearly", "age"]

schema = with_positional_mappings(infer_schema(df), feature_names)
