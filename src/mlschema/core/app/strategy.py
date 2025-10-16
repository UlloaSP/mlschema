from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from pandas import Series

from mlschema.core.domain import BaseField
from mlschema.core.util import normalize_dtype


class Strategy:
    """
    Abstract base class for all MLSchema field strategies.

    Each concrete strategy maps a *single* pandas dtype (or group of dtypes) to a
    validated JSON field specification. Strategies are **opt-in**: they influence
    schema generation only after being registered via `MLSchema.register()`.

    Usage contract:
        * Do **not** mutate the incoming `Series`; treat it as read-only.
        * Subclasses should override `attributes_from_series()` to emit extra
        metadata, but must avoid the reserved keys: `"title"`, `"type"`,
        `"required"`, `"description"`.
        * Registration is idempotent—duplicate `type_name`'s must be replaced via
        `MLSchema.update()`.
    """

    def __init__(
        self,
        *,
        type_name: str,
        schema_cls: type[BaseField],
        dtypes: Sequence[str | Any],
    ) -> None:
        """

        Args:
            type_name:  Identifier for the strategy type.
            schema_cls: Pydantic class that models the field.
            dtypes:     Sequence of ``dtype`` (instances or names) to which the strategy applies.
        """
        self._type_name: str = type_name
        self._schema_cls: type[BaseField] = schema_cls
        self._dtypes: tuple[str, ...] = tuple(
            normalize_dtype(dtype) for dtype in dtypes
        )

    @property
    def type_name(self) -> str:
        """Identifier for the strategy type."""
        return self._type_name

    @property
    def schema_cls(self) -> type[BaseField]:
        """Pydantic class used to serialize the schema."""
        return self._schema_cls

    @property
    def dtypes(self) -> tuple[str, ...]:
        """Tuple of supported ``dtype`` names."""
        return self._dtypes

    def attributes_from_series(self, series: Series) -> dict:
        """Calculate field-specific attributes.

        This method can be overridden by subclasses to add
        implementation-specific metadata to the schema.

        Args:
            series: Dataframe column to analyze.

        Returns:
            Dictionary with additional attributes; never includes the standard keys ``title``, ``type``, ``required``, ``description``.
        """
        return {}

    def build_dict(self, series: Series) -> dict:
        """Create the JSON representation of the schema.

        Combines the standard attributes with those returned by `attributes_from_series` and serializes the result with the associated Pydantic class.

        Args:
            series: Dataframe column to analyze.

        Returns:
            JSON with the field schema.
        """
        base_attrs: dict = {
            "title": series.name,
            "required": not series.isna().any(),
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
