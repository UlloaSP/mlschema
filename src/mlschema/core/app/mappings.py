"""Explicit conversion from named schema mappings to model input positions."""

from collections.abc import Sequence
from copy import deepcopy

from mlschema.core.app.kind import FieldDict


def with_positional_mappings(
    fields: Sequence[FieldDict], feature_names: Sequence[str]
) -> list[FieldDict]:
    """Copy fields, replacing named targets with ordered feature positions.

    Labels, series columns and one-hot grouping stay unchanged. Existing integer
    targets are accepted if in range. Neither the schema nor names are mutated.
    Raises ValueError for duplicate/empty names or missing/unknown targets.
    This converts mappings only; use infer_schema() to validate field schemas.
    """
    if isinstance(feature_names, str) or any(
        not isinstance(name, str) or not name for name in feature_names
    ):
        raise ValueError("feature_names must contain nonempty strings.")
    positions = {name: index for index, name in enumerate(feature_names)}
    if len(positions) != len(feature_names):
        raise ValueError("feature_names must be unique.")
    result = deepcopy(list(fields))
    for field in result:
        targets = [field]
        if field.get("kind") == "onehot-category":
            targets = field.get("options")
            if not isinstance(targets, list) or not targets:
                raise ValueError("One-hot fields must have mapped options.")
        for target in targets:
            if not isinstance(target, dict):
                raise ValueError("Mapped fields and options must be dictionaries.")
            mapping = target.get("mappedTo")
            if isinstance(mapping, str) and mapping in positions:
                target["mappedTo"] = positions[mapping]
            elif type(mapping) is not int or not 0 <= mapping < len(positions):
                raise ValueError(f"Unknown feature target: {mapping!r}.")
    return result
