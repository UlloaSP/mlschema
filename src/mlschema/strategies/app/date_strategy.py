# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
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
        | kind        | `Literal["date"]`   | Fixed type for the strategy.               |
        | defaultValue| `str | None`        | Initial ISO date value of the field.       |
        | min         | `str | None`        | Minimum allowed ISO date.                  |
        | max         | `str | None`        | Maximum allowed ISO date.                  |
        | step        | `PositiveInt`       | Increment in days.                         |

    Model Restrictions:
        | Description           | Error Type            | Error Message                                     |
        | --------------------- | --------------------- | ------------------------------------------------- |
        | `min` ≤ `max`         | `PydanticCustomError` | `min {min} must be ≤ max {max}`                   |
        | `defaultValue` ≥ `min`| `PydanticCustomError` | `defaultValue must be ≥ min`                      |
        | `defaultValue` ≤ `max`| `PydanticCustomError` | `defaultValue must be ≤ max`                      |

    """

    def __init__(self) -> None:
        super().__init__(
            type_name=FieldTypes.DATE,
            schema_cls=DateField,
            dtypes=("datetime64[ns]", "datetime64"),
        )
