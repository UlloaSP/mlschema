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


df = pd.DataFrame({"wait": pd.to_timedelta([90, 45, 300], unit="s")})

schema = infer_schema(df, kinds=[kind(model=DurationField, infer=duration_builder)])
