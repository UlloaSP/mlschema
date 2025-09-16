from __future__ import annotations

from pandas import Series, api

from mlschema.core import Strategy
from mlschema.strategies.domain import FieldTypes, NumberField


class NumberStrategy(Strategy):
    """Instance of Strategy for number fields.

    Name:
        `number`

    Dtypes:
        | Name     | Type              |
        | -------- | ----------------- |
        | int64    | `Int64Dtype`      |
        | float64  | `Float64Dtype`    |
        | int32    | `Int32Dtype`      |
        | float32  | `Float32Dtype`    |

    Model Attributes:
        | Name        | Type                | Description                                |
        | ----------- | ------------------- | ------------------------------------------ |
        | type        | `Literal["number"]` | Fixed type for the strategy.               |
        | value       | `int | float | None`| The current value of the field.            |
        | step        | `float | int`       | Increment for numeric values.              |
        | min         | `int | float | None`| Minimum allowed value.                     |
        | max         | `int | float | None`| Maximum allowed value.                     |
        | unit        | `str | None`        | Unit of measurement for the numeric value. |
        | placeholder | `str | None`        | Placeholder text for the field.            |

    Model Restrictions:
        | Description           | Error Type            | Error Message                                     |
        | --------------------- | --------------------- | ------------------------------------------------- |
        | `min` ≤ `max`         | `PydanticCustomError` | `min {min} must be ≤ max {max}`                   |
        | `value` ≥ `min`       | `PydanticCustomError` | `value {value} must be ≥ min {min}`               |
        | `value` ≤ `max`       | `PydanticCustomError` | `value {value} must be ≤ max {max}`               |

    """

    def __init__(self) -> None:
        super().__init__(
            type_name=FieldTypes.NUMBER,
            schema_cls=NumberField,
            dtypes=("int64", "float64", "int32", "float32"),
        )

    def attributes_from_series(self, series: Series) -> dict:
        """Derives the ``step`` attribute from the ``dtype``.

        Args:
            series: Pandas series with numeric values.

        Returns:
            Dictionary with the ``step`` key.
        """
        # Default step: 0.1 for floats, 1 for integers
        step = 0.1 if api.types.is_float_dtype(series.dtype) else 1
        return {"step": step}
