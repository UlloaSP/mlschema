# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
"""DataFrame-to-field inference pipeline.

The public `infer_schema()` function coordinates user builders, custom strict
field kinds, builtin kinds, overrides, and Pydantic validation. The pipeline is
deterministic: builders run in order and the first non-`None` field dict wins.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from pandas import DataFrame, Series
from pydantic import ValidationError

from mlschema.core.app.kind import (
    FieldBuilder,
    FieldContext,
    FieldDict,
    FieldKind,
    MappedToTarget,
)
from mlschema.core.exceptions import (
    EmptyDataFrameError,
    FieldBuilderError,
    FieldKindAlreadyRegisteredError,
    UnknownFieldKindError,
)
from mlschema.core.util import normalize_dtype
from mlschema.strategies.app import builtin_kinds
from mlschema.strategies.domain import FieldTypes
from mlschema.strategies.domain.series_field import add_series_sub_field


def infer_schema(
    df: DataFrame,
    *,
    builders: Sequence[FieldBuilder] = (),
    kinds: Sequence[FieldKind] = (),
    overrides: Mapping[str, Mapping[str, Any]] | None = None,
    onehot_separator: str = "__",
) -> list[FieldDict]:
    """Infer a strict field-list schema from a pandas DataFrame.

    Args:
        df: Source DataFrame. Each column becomes one field in output order.
        builders: Optional callables that can customize inference for already
            registered kinds. These run before custom kind builders and builtins.
        kinds: Optional strict custom field kinds created with `kind()`. Each
            kind contributes a Pydantic validator model and an inference builder.
        overrides: Optional mapping of column name to final field patch. Patches
            are applied after builder inference and before Pydantic validation.
        onehot_separator: Separator for one-hot columns, e.g. `feature__value`.

    Returns:
        JSON-serialisable list of validated field dictionaries.

    Raises:
        EmptyDataFrameError: If `df` has no rows or no columns.
        FieldKindAlreadyRegisteredError: If two kinds share the same name.
        FieldBuilderError: If an override targets a missing column, a builder
            returns invalid data, or no builder matches a column.
        UnknownFieldKindError: If a builder emits a kind with no registered
            model.
        pydantic.ValidationError: If generated or overridden field data violates
            the target field model.
    """
    if df.columns.empty or df.empty:
        raise EmptyDataFrameError(df)
    targets = _mapped_targets(df)
    labels = _labels(df)

    all_kinds = (*kinds, *builtin_kinds())
    models = _models_by_kind(all_kinds)
    infer_builders = (*builders, *(item.infer for item in all_kinds))
    overrides = overrides or {}
    _check_override_columns(df, overrides)

    onehot_groups = _onehot_groups(df, labels, targets, onehot_separator)
    consumed = {index for group in onehot_groups.values() for index, _, _ in group}

    def infer_field(series: Series, index: int = 0) -> FieldDict:
        label = (
            labels[index]
            if str(series.name) == str(df.columns[index])
            else str(series.name)
        )
        ctx = FieldContext(
            name=label,
            dtype=normalize_dtype(series.dtype),
            required=not series.isna().any(),
            index=index,
            mappedTo=targets[index],
            infer_field=lambda sub_series: infer_field(sub_series, index),
        )
        raw = _first_field(series, ctx, infer_builders)
        if str(series.name) in overrides:
            raw = {**raw, **overrides[str(series.name)]}
        return _validate_field(raw, models)

    fields: list[FieldDict] = []
    emitted_groups: set[str] = set()
    for index, (_, series) in enumerate(df.items()):
        group_name = _group_name(index, onehot_groups)
        if group_name is not None:
            if group_name not in emitted_groups:
                fields.append(
                    _validate_field(
                        _onehot_field(group_name, onehot_groups[group_name]), models
                    )
                )
                emitted_groups.add(group_name)
            continue
        if index not in consumed:
            fields.append(infer_field(series, index))
    return fields


def _mapped_targets(df: DataFrame) -> list[MappedToTarget]:
    if _has_positional_columns(df):
        return list(range(len(df.columns)))
    return [str(column) for column in df.columns]


def _labels(df: DataFrame) -> list[str]:
    if _has_positional_columns(df):
        return [f"feature_{index}" for index in range(len(df.columns))]
    return [str(column) for column in df.columns]


def _has_positional_columns(df: DataFrame) -> bool:
    return list(df.columns) == list(range(len(df.columns)))


def _onehot_groups(
    df: DataFrame,
    labels: Sequence[str],
    targets: Sequence[MappedToTarget],
    separator: str,
) -> dict[str, list[tuple[int, str, MappedToTarget]]]:
    if separator == "":
        raise FieldBuilderError(
            "onehot_separator", separator, "Separator cannot be empty."
        )
    groups: dict[str, list[tuple[int, str, MappedToTarget]]] = {}
    for index, label in enumerate(labels):
        if separator not in label or not _is_binary(df.iloc[:, index]):
            continue
        prefix, value = label.split(separator, 1)
        if prefix and value:
            groups.setdefault(prefix, []).append((index, value, targets[index]))
    return {name: options for name, options in groups.items() if len(options) > 1}


def _is_binary(series: Series) -> bool:
    values = set(series.dropna().unique())
    return bool(values) and values <= {0, 1}


def _group_name(
    index: int, groups: Mapping[str, Sequence[tuple[int, str, MappedToTarget]]]
) -> str | None:
    for name, options in groups.items():
        if any(item[0] == index for item in options):
            return name
    return None


def _onehot_field(
    name: str, options: Sequence[tuple[int, str, MappedToTarget]]
) -> FieldDict:
    return {
        "kind": str(FieldTypes.ONEHOT_CATEGORY),
        "label": name,
        "required": True,
        "description": None,
        "options": [
            {"label": value, "value": value, "mappedTo": target}
            for _, value, target in options
        ],
    }


def _models_by_kind(kinds: Sequence[FieldKind]) -> dict[str, type]:
    """Build the validation model map for active kinds.

    Args:
        kinds: Builtin and custom kind definitions.

    Returns:
        Mapping from field-kind name to Pydantic model.

    Raises:
        FieldKindAlreadyRegisteredError: If a kind name appears more than once.
    """
    models: dict[str, type] = {}
    for item in kinds:
        if item.name in models:
            raise FieldKindAlreadyRegisteredError(item.name)
        models[item.name] = item.model
        if item.name != FieldTypes.SERIES:
            add_series_sub_field(item.model)
    return models


def _check_override_columns(
    df: DataFrame, overrides: Mapping[str, Mapping[str, Any]]
) -> None:
    """Validate that all override targets exist in the DataFrame.

    Args:
        df: Source DataFrame.
        overrides: Final field patches keyed by column name.

    Raises:
        FieldBuilderError: If any override key is missing from `df.columns`.
    """
    missing = sorted(set(overrides) - {str(column) for column in df.columns})
    if missing:
        raise FieldBuilderError(
            "overrides",
            missing,
            "Overrides reference columns that are not in the DataFrame.",
        )


def _first_field(
    series: Series,
    ctx: FieldContext,
    builders: Sequence[FieldBuilder],
) -> FieldDict:
    """Run builders and return the first claimed field.

    Args:
        series: Source column.
        ctx: Field context for the source column.
        builders: Ordered builder callables.

    Returns:
        First field dict emitted by a builder.

    Raises:
        FieldBuilderError: If a builder returns a non-dict value, or no builder
            claims the column.
    """
    for builder in builders:
        raw = builder(series, ctx)
        if raw is None:
            continue
        if not isinstance(raw, dict):
            raise FieldBuilderError(
                "builder",
                builder,
                "Field builder must return a dict or None.",
            )
        return raw
    raise FieldBuilderError("builders", builders, "No field builder matched column.")


def _validate_field(raw: FieldDict, models: Mapping[str, type]) -> FieldDict:
    """Validate and serialise a raw field dict.

    Args:
        raw: Field dict emitted by a builder and patched by overrides.
        models: Mapping from field-kind name to Pydantic model.

    Returns:
        JSON-serialisable field dict produced by Pydantic.

    Raises:
        FieldBuilderError: If `raw` omits the `kind` key.
        UnknownFieldKindError: If `raw["kind"]` has no registered model.
        pydantic.ValidationError: If the model rejects the field.
    """
    raw_kind = raw.get("kind")
    if raw_kind is None:
        raise FieldBuilderError("kind", raw, "Field builder output must include kind.")
    model = models.get(str(raw_kind))
    if model is None:
        raise UnknownFieldKindError(str(raw_kind))
    try:
        return model(**raw).model_dump(
            mode="json",
            exclude_unset=False,
            exclude_none=True,
        )
    except ValidationError:
        raise
