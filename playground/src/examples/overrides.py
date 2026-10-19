import pandas as pd

from mlschema import infer_schema

df = pd.DataFrame(
    {
        "name": ["Ada", "Linus"],
        "score": [98.5, 86.0],
        "active": [True, False],
    }
)

# Overrides patch top-level attributes after inference, then Pydantic validates
# the result. Try "min": 200 to see a validation error.
infer_schema(
    df,
    overrides={
        "name": {"label": "Full name", "placeholder": "Ada Lovelace", "maxLength": 80},
        "score": {"label": "Score", "min": 0, "max": 100, "unit": "points"},
        "active": {"label": "Enabled", "trueLabel": "Yes", "falseLabel": "No"},
    },
)
