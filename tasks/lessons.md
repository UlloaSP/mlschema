# Lessons

- Read current `AGENTS.md` every turn; repo debt path is `tasks/debt.md`.
- Keep package version single-source in `pyproject.toml`; CI should parse that file, not import package-level constants.
- When editing a file with an explicit `Last Updated` / last-modified date, update that date in the same change.
- For Python tasks, always run commands through `uv`, and verify with `ruff` plus `pyright`.
- Keep tool config single-source when supported; prefer `pyproject.toml` over parallel tool-specific config files.
- When changelog content is suspect, derive entries from tags and commit ranges instead of editing existing sections in place.
- Prefer adding new accepted dtypes to owning strategies over hiding semantic compatibility in global dtype normalization.
