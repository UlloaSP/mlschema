from typing import Literal

import pandas as pd
from pandas import Series

from mlschema import BaseField, FieldContext, infer_schema, kind


class DurationField(BaseField):
    kind: Literal["duration"] = "duration"
    unit: Literal["seconds"] = "seconds"
    minSeconds: int
    maxSeconds: int


def duration_builder(series: Series, ctx: FieldContext) -> dict | None:
    if not ctx.dtype.startswith("timedelta64"):
        return None
    return {
        "kind": "duration",
        "label": ctx.name,
        "required": ctx.required,
        "mappedTo": ctx.mappedTo,
        "minSeconds": int(series.min().total_seconds()),
        "maxSeconds": int(series.max().total_seconds()),
    }


def money_builder(series: Series, ctx: FieldContext) -> dict | None:
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


df = pd.DataFrame(
    {
        "amount_eur": [12.5, 30.0],
        "duration": pd.to_timedelta(["90s", "1h"]),
    }
)

infer_schema(
    df,
    builders=[money_builder],
    kinds=[kind(model=DurationField, infer=duration_builder)],
)
