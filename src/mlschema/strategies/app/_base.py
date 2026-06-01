# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Pablo Ulloa Santin
"""Shared helpers for builtin field builders.

This module contains only low-level utilities used by individual builtin
builders. It is intentionally private: the public extension surface is the
`FieldBuilder` callable protocol exposed from `mlschema`.
"""

from __future__ import annotations

from mlschema.core.app.kind import FieldContext, FieldDict


def base_field(ctx: FieldContext, kind_name: str) -> FieldDict:
    """Build common field attributes for a generated field.

    Args:
        ctx: Column metadata supplied by `infer_schema`.
        kind_name: Field kind discriminator to place in the output dict.

    Returns:
        Dict containing the reserved field keys populated by MLSchema:
        `kind`, `label`, `required`, and `description`.
    """
    return {
        "kind": str(kind_name),
        "label": ctx.name,
        "required": ctx.required,
        "description": None,
    }
