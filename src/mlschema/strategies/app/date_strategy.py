from __future__ import annotations

from mlschema.core import Strategy
from mlschema.strategies.domain import DateField, FieldTypes


class DateStrategy(Strategy):
    """Instance of Strategy for date fields.

    Name:
        `date`

    Dtypes:
        | Name           | Type                |
        | -------------- | ------------------- |
        | datetime64[ns] | `DatetimeTZDtype`   |
        | datetime64     | `DatetimeDtype`     |

    Model Attributes:
        | Name        | Type                | Description                                |
        | ----------- | ------------------- | ------------------------------------------ |
        | type        | `Literal["date"]`   | Fixed type for the strategy.               |
        | value       | `date | None`       | The current value of the field.            |
        | min         | `date | None`       | Minimum allowed date.                      |
        | max         | `date | None`       | Maximum allowed date.                      |
        | step        | `PositiveInt`       | Increment in days.                         |

    Model Restrictions:
        | Description           | Error Type            | Error Message                                     |
        | --------------------- | --------------------- | ------------------------------------------------- |
        | `min` ≤ `max`         | `PydanticCustomError` | `min {min} must be ≤ max {max}`                   |
        | `value` ≥ `min`       | `PydanticCustomError` | `value {value} must be ≥ min {min}`               |
        | `value` ≤ `max`       | `PydanticCustomError` | `value {value} must be ≤ max {max}`               |

    """

    def __init__(self) -> None:
        super().__init__(
            type_name=FieldTypes.DATE,
            schema_cls=DateField,
            dtypes=("datetime64[ns]", "datetime64"),
        )
