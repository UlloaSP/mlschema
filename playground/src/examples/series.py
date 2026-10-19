import pandas as pd

from mlschema import infer_schema

# Cells holding two values (tuples, lists or two-key dicts) become a series
# field with one column per value.
df = pd.DataFrame(
    {
        "reading": [
            (pd.Timestamp("2024-01-01"), 23.5),
            (pd.Timestamp("2024-01-02"), 24.1),
        ],
        "dose": [
            {"time": "2024-01-01", "mg": 5},
            {"time": "2024-01-02", "mg": 7},
        ],
    }
)

infer_schema(df, overrides={"reading": {"label": "Sensor reading", "maxPoints": 100}})
