"""Series columns reuse field-kind validation without backend mappings."""

from typing import Any

from pydantic_core import PydanticCustomError

from mlschema.core.domain import BaseField
from mlschema.strategies.domain.boolean_field import BooleanField
from mlschema.strategies.domain.category_field import CategoryField
from mlschema.strategies.domain.date_field import DateField
from mlschema.strategies.domain.field_types import FieldTypes
from mlschema.strategies.domain.number_field import NumberField
from mlschema.strategies.domain.text_field import TextField

_COLUMN_KINDS: dict[str, type[BaseField]] = {
    FieldTypes.BOOLEAN: BooleanField,
    FieldTypes.CATEGORY: CategoryField,
    FieldTypes.DATE: DateField,
    FieldTypes.NUMBER: NumberField,
    FieldTypes.TEXT: TextField,
}


def add_series_sub_field(cls: type[BaseField]) -> None:
    """Reuse a custom scalar kind's validators inside series columns."""
    kind_name = str(cls.model_fields["kind"].default)
    if kind_name in (FieldTypes.SERIES, FieldTypes.ONEHOT_CATEGORY):
        raise ValueError("Series columns must be scalar field kinds.")
    _COLUMN_KINDS[kind_name] = cls


def parse_column(value: Any) -> dict[str, Any]:
    """Validate column properties through their owning strict field model."""
    if not isinstance(value, dict) or "mappedTo" in value:
        raise PydanticCustomError(
            "invalid_series_column", "Series columns must be dicts without mappedTo"
        )
    properties = dict(value)
    column_id = properties.pop("id", None)
    if column_id not in ("field1", "field2"):
        raise PydanticCustomError(
            "invalid_series_column_id", "Series column id must be field1 or field2"
        )
    model = _COLUMN_KINDS.get(str(properties.get("kind", "")))
    if model is None:
        raise PydanticCustomError(
            "invalid_series_column_kind", "Unknown or non-scalar series column kind"
        )
    # A column uses its local id while borrowing the owning field validators.
    validated = model(**properties, mappedTo=column_id)
    return {
        **validated.model_dump(mode="json", exclude_none=True, exclude={"mappedTo"}),
        "id": column_id,
    }
