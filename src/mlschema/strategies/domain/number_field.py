"""mlschema.strategies.domain.number_field
========================================
Pydantic model for **numeric** fields (integers or floats).

Based on :class:`mlschema.core.domain.BaseField`, adds the following
attributes:

* ``min`` / ``max`` - Lower and upper allowed bounds.
* ``step``          - Default increment (``1`` if not specified).
* ``placeholder``   - Guide text for the front-end.
* ``value``         - Current value (optional).
* ``unit``          - Unit of measurement (e.g. "kg", "€").

The ``_check_numeric_constraints`` validator ensures consistency between
bounds and value.
"""

from __future__ import annotations

from typing import Literal

from pydantic import model_validator

from mlschema.core.domain import BaseField
from mlschema.strategies.domain.field_types import FieldTypes


class NumberField(BaseField):
    """Pydantic schema for a numeric field."""

    type: Literal[FieldTypes.NUMBER] = FieldTypes.NUMBER
    min: float | None = None
    max: float | None = None
    step: float | None = 1
    placeholder: str | None = None
    value: float | None = None
    unit: str | None = None

    @model_validator(mode="after")
    def _check_numeric_constraints(self) -> NumberField:
        """Validates that *min* ≤ *value* ≤ *max*.

        Returns
        -------
        NumberField
            Validated instance.

        Raises
        ------
        ValueError
            If bounds are not consistent.
        """
        if self.min is not None and self.max is not None and self.min > self.max:
            raise ValueError(f"min ({self.min}) must be ≤ max ({self.max})")

        if self.value is not None:
            if self.min is not None and self.value < self.min:
                raise ValueError(f"value ({self.value}) must be ≥ min ({self.min})")
            if self.max is not None and self.value > self.max:
                raise ValueError(f"value ({self.value}) must be ≤ max ({self.max})")
        return self
