from __future__ import annotations

from mlschema.core import Strategy
from mlschema.strategies.domain import FieldTypes, TextField


class TextStrategy(Strategy):
    """Instance of Strategy for text fields.

    Name:
        `text`

    Dtypes:
        | Name     | Type              |
        | -------- | ----------------- |
        | object   | `object`          |
        | string   | `StringDtype`     |

    Model Attributes:
        | Name        | Type              | Description                                |
        | ----------- | ----------------- | ------------------------------------------ |
        | type        | `Literal["text"]` | Fixed type for the strategy.               |
        | value       | `str | None`      | The current value of the field.            |
        | placeholder | `str | None`      | Placeholder text for the field.            |
        | min_length  | `int | None`      | Minimum length of the text.                |
        | max_length  | `int | None`      | Maximum length of the text.                |
        | pattern     | `str | None`      | Regular expression pattern for validation. |

    Model Restrictions:
        | Description                   | Error Type            | Error Message                                                 |
        | ----------------------------- | --------------------- | ------------------------------------------------------------- |
        | `min_length` ≤ `max_length`   | `PydanticCustomError` | `minLength {minLength} must be ≤ maxLength {maxLength}`       |
        | `value` length ≥ `min_length` | `PydanticCustomError` | `value length {value_length} must be ≥ minLength {minLength}` |
        | `value` length ≤ `max_length` | `PydanticCustomError` | `value length {value_length} must be ≤ maxLength {maxLength}` |

    """

    def __init__(self) -> None:
        super().__init__(
            type_name=FieldTypes.TEXT,
            schema_cls=TextField,
            dtypes=("object", "string"),
        )
