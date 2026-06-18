- [x] Add strict MLSchema `mappedTo` target contract (`str | int`) for generated fields.
- [x] Add `onehot-category` field model and inference from separator-grouped feature columns.
- [x] Add tests for required mapped targets, onehot grouping, and positional fallback.
- [x] Update docs/test/debt memory for the new schema contract.
- [x] Run focused tests, lint, typecheck, and graph update.
- [x] Remove unnecessary `feature_names` argument from `infer_schema()`.
- [x] Keep DataFrame columns as schema labels and onehot grouping source.
- [x] Make default `mappedTo` targets original zero-based input positions.
- [x] Update tests, docs, debt, and lessons for the corrected contract.
- [x] Run focused verification and graph update.
- [x] Remove unnecessary `mapped_to` argument from `infer_schema()`.
- [x] Derive `mappedTo` from DataFrame columns: string for named columns, int for positional columns.
- [x] Generate `feature_<position>` labels for positional DataFrame columns.
- [x] Update tests, docs, script, and memory for the final inferred mapping contract.
- [x] Re-run verification and graph update.
- [x] Clarify onehot grouping only applies to named encoded feature columns.
- [x] Add regression proving positional binary columns stay ordinary fields.
- [x] Re-run focused verification and graph update.

## Review

- Added mandatory `mappedTo` for normal fields.
- Added `onehot_separator` to `infer_schema()`.
- Added `onehot-category` output with backend targets on `options[]`.
- Removed `feature_names` and `mapped_to`; DataFrame columns now own labels, onehot names, and backend targets.
- Verification passed: `uv run python check_mappedto_onehot.py`, focused pytest, `uv run pytest`, focused ruff, `uv run ruff check .`, `uv run pyright`, `uv run mkdocs build --strict`, `graphify update .`, `git diff --check`.
- Final mapping correction: `infer_schema()` has no feature/mapping argument; named columns map to strings, positional columns map to ints with `feature_<position>` labels.
- Onehot correction: grouping needs named encoded feature columns; positional binary columns remain ordinary fields with integer `mappedTo`.
