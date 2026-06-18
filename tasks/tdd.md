# Test Map

Quick overview of the active MLSchema test suite.

## Rule

- If any file under `test/` changes, update this file in the same change.
- Keep this map aligned with test scope, names, and intent.
- Add new suites here before considering test work complete.

## Organization

| Path | Scope | Validates |
| ---- | ----- | --------- |
| `test/unit/test_base_field_contract.py` | Unit | `BaseField` shared contract: required `mappedTo`, accepted optional attributes, invalid labels/descriptions/targets/extra keys. |
| `test/unit/test_builtin_builders.py` | Unit | Direct builder behavior for boolean, category, date, number, series, and text fallback. |
| `test/unit/test_builtin_dtype_matrix.py` | Unit | Supported and rejected dtype matrix for builtin builders, plus text fallback totality. |
| `test/unit/test_builtin_edge_cases.py` | Unit | Builder edge cases: category option extraction, numeric edge values, series pair shapes, malformed series cells, sub-series coercion. |
| `test/unit/test_dtype_normalization.py` | Unit | `normalize_dtype()` branches for pandas, extension, raw string, structured, named, and fallback values. |
| `test/unit/test_factory_and_context.py` | Unit | Builtin kind order, builder callability, and `FieldContext` metadata including `mappedTo`. |
| `test/unit/test_field_models.py` | Unit | Builtin Pydantic model success cases and constraint failures for boolean/category/onehot-category/date/number/series/text. |
| `test/unit/test_inference_errors.py` | Unit | Known inference exceptions: empty DataFrame, invalid onehot separator, missing overrides, invalid builder output, missing/unknown kind, duplicate kind, validation failures, root exception inheritance. |
| `test/unit/test_kind_api.py` | Unit | `kind()` API: kind-name extraction from model and non-`BaseField` rejection. |
| `test/integration/test_infer_schema_workflows.py` | Integration | End-to-end workflows with all builtins, overrides, custom builder, custom strict kind, named-column mapping, onehot grouping from named encoded feature columns, and positional fallback with generated labels. |
| `test/integration/test_schema_output_matrix.py` | Integration | End-to-end output matrix for builtin dtype families and supported series shapes. |
| `test/architecture/test_public_surface.py` | Architecture | Public API surface, builtin module split, exception module split, no imports from removed modules. |
| `test/architecture/test_test_suite_structure.py` | Architecture | Test suite folder organization, test file line limits, and no removed public class API usage in tests. |
| `test/load/test_infer_schema_load.py` | Load | Inference correctness under many rows/columns, named-column mapping, and large categorical option sets. |

## Current Coverage Shape

- Pytest items: 216.
- Suite scopes: unit, integration, architecture, load.
- Every active test file is under 300 lines.
- Removed API leak checks cover old class/registry/service modules and public class API names.

## Commands

```bash
uv run pytest
uv run ruff check .
uv run pyright
uv run mkdocs build --strict
uv run pre-commit run --all-files
uv build
```
