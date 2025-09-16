"""
FieldStrategy
================================
Strategies for deriving metadata from a column (``pandas.Series``) and
materializing them into a Pydantic schema.

The :class:`FieldStrategy` class serves as a base class for specific
data type strategies (number, text, date, etc.). Each strategy defines:

* ``type_name``  - Logical identifier for the type (``"number"``, ``"text"``, …).
* ``schema_cls`` - Subclass of :class:`mlschema.core.domain.BaseField`
  used to serialize the result.
* ``dtypes``     - Set of NumPy / pandas dtypes for which the
  strategy is valid.

Example Usage
-------------
```python
 import pandas as pd
 from mlschema.core.domain import NumberField
 class NumberStrategy(FieldStrategy):
     def __init__(self) -> None:
         super().__init__(
             type_name="number",
             schema_cls=NumberField,
             dtypes=("float64", "int64"),
         )

     def attributes_from_series(self, series: pd.Series) -> dict:
         'Derives basic attributes: minimum and maximum.'
         return {"min": float(series.min()), "max": float(series.max())}
 s = pd.Series([1, 2, 3], name="age", dtype="int64")
 NumberStrategy().build_dict(s)
'{"title":"age","required":true,"description":null,"type":"number","min":1.0,"max":3.0}'
```
"""

from __future__ import annotations

from collections.abc import Sequence

from numpy import dtype as np_dtype
from pandas import Series, api

from mlschema.core.domain import BaseField


class FieldStrategy:
    """Base contract for all field strategies.

    Each subclass should (optionally) override
    :meth:`attributes_from_series` to add specific metadata to
    the generated schema.

    Attributes
    ----------
    _type_name:
        Logical identifier for the field type.
    _schema_cls:
        Subclass of :class:`BaseField` used for serialization.
    _dtypes:
        Tuple of ``dtype`` names compatible with the strategy.
    """

    # -------------------------- construction --------------------------- #
    def __init__(
        self,
        *,
        type_name: str,
        schema_cls: type[BaseField],
        dtypes: Sequence[str | np_dtype],
    ) -> None:
        """Initialize the strategy.

        Parameters
        ----------
        type_name:
            Logical identifier for the type (e.g. ``"number"``).
        schema_cls:
            Pydantic class that models the field.
        dtypes:
            Sequence of ``dtype`` (instances or names) to which the strategy applies.
        """
        self._type_name: str = type_name
        self._schema_cls: type[BaseField] = schema_cls
        # Normalize dtypes to ``str`` for future comparisons
        self._dtypes: tuple[str, ...] = tuple(
            dt.name
            if isinstance(dt, np_dtype | api.extensions.ExtensionDtype)
            else str(dt)
            for dt in dtypes
        )

    # -------------------------- properties ----------------------------- #
    @property
    def type_name(self) -> str:
        """Logical name of the field type."""
        return self._type_name

    @property
    def schema_cls(self) -> type[BaseField]:
        """Pydantic class used to serialize the schema."""
        return self._schema_cls

    @property
    def dtypes(self) -> tuple[str, ...]:
        """Tuple of supported ``dtype`` names."""
        return self._dtypes

    # -------------------- optional extension point ------------------- #
    def attributes_from_series(self, series: Series) -> dict:
        """Calculate field-specific attributes.

        This method can be overridden in each concrete strategy
        to derive attributes like ``min``, ``max``, ``options``, etc.

        Parameters
        ----------
        series:
            Pandas column to analyze.

        Returns
        -------
        dict
            Dictionary with additional attributes; never includes the
            standard keys ``title``, ``required``, ``description`` or ``type``.
        """
        return {}

    # -------------------- complete payload factory ------------------- #
    def build_dict(self, series: Series) -> dict:
        """Create the JSON representation of the schema.

        Combines standard attributes with those returned by
        :meth:`attributes_from_series` and serializes the result with the
        associated Pydantic class.

        Parameters
        ----------
        series:
            Pandas column to document.

        Returns
        -------
        dict
            JSON with the field schema.
        """
        base_attrs: dict = {
            "title": series.name,
            "required": series.notnull().all(),
            "description": None,
            "type": self.type_name,
        }
        # Incorporate implementation-specific attributes
        base_attrs.update(self.attributes_from_series(series))

        # Instantiate the Pydantic class and dump to JSON
        return self._schema_cls(**base_attrs).model_dump(
            mode="json",
            exclude_unset=False,
            exclude_none=True,
        )
