- [x] Restore coverage depth lost during test rewrite.
- [x] Add granular parametrized unit tests for builtin dtype matching and edge cases.
- [x] Add granular model constraint and dtype normalization tests.
- [x] Add integration, architecture, and load matrix tests without legacy leaks.
- [x] Update debt/todo review and lessons.
- [x] Run `uv` tests, `ruff`, `pyright`, docs build, pre-commit, build, and graphify update.

## Review

- Expanded modular suite from 37 to 215 pytest items.
- Added granular dtype matrix tests for boolean, number, date, category, and text builders.
- Added edge-case tests for category options, numeric edge values, series shapes, series coercion, dtype normalization, BaseField attributes, factory order, and FieldContext metadata.
- Added integration output matrix for every builtin dtype family and series shape.
- Added architecture tests for test layout, line limits, and removed public API leaks.
- Verification passed: `uv run pytest`, `uv run ruff check .`, `uv run pyright`, `uv run mkdocs build --strict`, `uv run pre-commit run --all-files`, `uv build`, `graphify update .`.
