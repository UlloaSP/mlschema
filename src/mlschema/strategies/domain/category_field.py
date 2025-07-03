"""mlschema.strategies.domain.category_field
===========================================
Pydantic model for **categorical** fields.

Extends :class:`mlschema.core.domain.BaseField` by fixing the
``type`` attribute to ``"category"`` and adding:

* ``value``   - Current value (optional).
* ``options`` - List of allowed categories (minimum 1 element).

The ``_check_value_in_options`` validator ensures that, if ``value`` is specified,
it appears within ``options``.

"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field, model_validator

from mlschema.core.domain import BaseField
from mlschema.strategies.domain.field_types import FieldTypes


class CategoryField(BaseField):
    """Pydantic schema for a categorical field."""

    type: Literal[FieldTypes.CATEGORY] = FieldTypes.CATEGORY
    value: str | None = None
    options: Annotated[list[str], Field(min_length=1)]

    @model_validator(mode="after")
    def _check_value_in_options(self) -> CategoryField:
        """Validates that ``value`` is within ``options``.

        Returns
        -------
        CategoryField
            Valid instance.

        Raises
        ------
        ValueError
            If ``value`` is not in ``options``.
        """
        if self.value is not None and self.value not in self.options:
            raise ValueError("Value must match one of the allowed options")
        return self
