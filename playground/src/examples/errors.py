import pandas as pd
from pydantic import ValidationError

from mlschema import infer_schema
from mlschema.core.exceptions import EmptyDataFrameError, FieldBuilderError

df = pd.DataFrame({"score": [98.5, 86.0]})
cases = {
    "empty DataFrame": lambda: infer_schema(pd.DataFrame()),
    "unknown override column": lambda: infer_schema(df, overrides={"age": {}}),
    "invalid bounds": lambda: infer_schema(
        df, overrides={"score": {"min": 10, "max": 1}}
    ),
}

report = []
for case, call in cases.items():
    try:
        call()
    except (EmptyDataFrameError, FieldBuilderError, ValidationError) as error:
        print(f"{case}: {type(error).__name__}")
        report.append(
            {"case": case, "error": type(error).__name__, "message": str(error)}
        )

# Uncaught exceptions appear below the result with their traceback. Try:
# infer_schema(pd.DataFrame())
report  # pyright: ignore[reportUnusedExpression]
