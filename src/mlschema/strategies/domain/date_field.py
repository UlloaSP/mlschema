"""mlschema.strategies.domain.date_field
=======================================
Pydantic model for **date** fields.

Extends :class:`mlschema.core.domain.BaseField` by fixing the
``type`` attribute to ``"date"`` and adding specific metadata:

* ``value`` - Selected date (optional).
* ``min``   - Minimum allowed date.
* ``max``   - Maximum allowed date.
* ``step``  - Increment in days (``PositiveInt``).

The ``_check_dates`` validator enforces internal consistency between ``min``,
``max`` and ``value``.
"""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import PositiveInt, model_validator

from mlschema.core.domain import BaseField
from mlschema.strategies.domain.field_types import FieldTypes


class DateField(BaseField):
    """Pydantic schema for a date/time field."""

    type: Literal[FieldTypes.DATE] = FieldTypes.DATE
    value: date | None = None
    min: date | None = None
    max: date | None = None
    step: PositiveInt = 1

    @model_validator(mode="after")
    def _check_dates(self) -> DateField:
        """Validates consistency between *min*, *max* and *value*.

        Returns
        -------
        DateField
            Validated instance.

        Raises
        ------
        ValueError
            If dates are inconsistent.
        """
        if self.min and self.max and self.min > self.max:
            raise ValueError(
                "Minimum date must be earlier than or equal to maximum date"
            )

        if self.value:
            if self.min and self.value < self.min:
                raise ValueError("Date must be later than or equal to minimum date")
            if self.max and self.value > self.max:
                raise ValueError("Date must be earlier than or equal to maximum date")
        return self
