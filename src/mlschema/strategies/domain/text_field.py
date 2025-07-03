"""mlschema.strategies.domain.text_field
======================================
Pydantic model for **text** fields.

Extends :class:`mlschema.core.domain.BaseField` by fixing ``type='text'`` and
providing optional length and pattern validation.

Additional attributes
---------------------
* ``value``       - Current value (optional).
* ``placeholder`` - Guide text for the front-end.
* ``minLength``   - Minimum allowed length.
* ``maxLength``   - Maximum allowed length.
* ``pattern``     - Python regular expression (as *string*).

The ``_check_lengths`` validator checks consistency between ``minLength``
and ``maxLength``.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from mlschema.core.domain import BaseField
from mlschema.strategies.domain.field_types import FieldTypes


class TextField(BaseField):
    """Pydantic schema for a text field."""

    type: Literal[FieldTypes.TEXT] = FieldTypes.TEXT
    value: str | None = None
    placeholder: str | None = None
    minLength: int | None = None
    maxLength: int | None = None
    pattern: str | None = Field(
        default=None,
        description=(
            "Regular expression in Python notation; Pydantic does not preserve "
            "re.Pattern instances in JSON serialization."
        ),
    )

    @model_validator(mode="after")
    def _check_lengths(self) -> TextField:
        """Validates that *minLength* ≤ *maxLength*.

        Returns
        -------
        TextField
            Validated instance.

        Raises
        ------
        ValueError
            If lengths are inconsistent.
        """
        if (
            self.minLength is not None
            and self.maxLength is not None
            and self.minLength > self.maxLength
        ):
            raise ValueError(
                f"minLength ({self.minLength}) must be ≤ maxLength ({self.maxLength})"
            )
        return self
