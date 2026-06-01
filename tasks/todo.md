- [x] Remove report/explanation domain code and exports.
- [x] Change build contract to return field list directly.
- [x] Update tests for unwrapped field list.
- [x] Update docs/README/changelog references.
- [x] Update dependency versions and lockfile.
- [x] Run verification and document result.
- [x] Remove duplicate package version source and update CI.
- [x] Rebuild changelog from git tags and commits.

## Review

- Removed report/explanation models, exports, and docs.
- `MLSchema.build()` now returns `list[dict]` directly.
- Updated dependencies/package version and regenerated local lock state.
- Verification passed: `uv run pytest`, `uv run ruff check .`, `uv run pyright`, `uv run mkdocs build --strict`.
- CI publish version now reads `pyproject.toml`; `src/mlschema/__init__.py` no longer stores duplicate version.
- Verification passed after CI update: `uv build`, `uv run pre-commit run --all-files`, `uv run pytest`.
