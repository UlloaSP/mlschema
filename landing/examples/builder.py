import pandas as pd
from pandas import Series

from mlschema import FieldContext, infer_schema


def money_builder(_series: Series, ctx: FieldContext) -> dict | None:
    if ctx.name != "amount_eur":
        return None
    return {
        "kind": "number",
        "label": "Amount",
        "required": ctx.required,
        "mappedTo": ctx.mappedTo,
        "step": 0.01,
        "unit": "EUR",
        "min": 0,
    }


df = pd.DataFrame({"amount_eur": [12.5, 80.0, 43.2]})

schema = infer_schema(df, builders=[money_builder])
