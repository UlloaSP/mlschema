from __future__ import annotations

from mlschema.core import Strategy
from mlschema.strategies.domain import BooleanField, FieldTypes


class BooleanStrategy(Strategy):
    """Instance of Strategy for boolean fields.

    Name:
        `boolean`

    Dtypes:
        | Name     | Type              |
        | -------- | ----------------- |
        | bool     | `BooleanDtype`    |
        | boolean  | `BooleanDtype`    |

    Model Attributes:
        | Name        | Type                 | Description                                |
        | ----------- | -------------------- | ------------------------------------------ |
        | type        | `Literal["boolean"]` | Fixed type for the strategy.               |
        | value       | `bool | None`        | The current value of the field.            |

    """

    def __init__(self) -> None:
        super().__init__(
            type_name=FieldTypes.BOOLEAN,
            schema_cls=BooleanField,
            dtypes=("bool", "boolean"),
        )
