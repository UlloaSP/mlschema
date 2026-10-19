# Contributing to MLschema

Use Python 3.14 and uv for the library. Websites use Vite+ (`vp`), backed by pnpm 12.
Supported Node.js versions: 22.18+, 24.11+, or 26+ (the corresponding major versions).

## Library

```bash
uv sync --locked --group dev
uv run pre-commit install
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
uv build
```

Start with the tests for the behavior you change, then run the full suite. Test both
success and error paths. Keep each source file at or below 300 lines. Update the
affected documentation when contracts or known limitations change; include actual
verification and any remaining blockers in the change description.

The public API starts at `mlschema.infer_schema`. Builders inspect pandas columns;
strict field models validate their output. Custom kinds pair a `BaseField` subclass
with a builder through `kind(model=..., infer=...)`. Keep rules in their owning
module so callers share them.

Series columns use local ids and scalar-kind validators. Only the parent maps to
a backend feature. `with_positional_mappings` converts named targets when a consumer
needs input positions; it preserves the original field list.

## Websites

```bash
vp install --frozen-lockfile
vp run dev:landing
vp run dev:docs
vp run dev:playground
vp run build
```

Landing, Astro Starlight documentation and the Python playground live in separate
workspace packages. Use the eshkra product identity and original assets under
`brand/`. Verify narrow/wide screens and both themes when changing presentation.

Local URLs: landing `http://127.0.0.1:4330`, docs `http://127.0.0.1:4331`,
playground `http://127.0.0.1:10011`. Start each dev task in its own terminal.
Install the [Vite+ CLI](https://viteplus.dev/guide/) first, or bootstrap with
`pnpm install --frozen-lockfile` and use `pnpm exec vp` for these commands.

## Release

`pyproject.toml` owns the Python package version. Update it and the documentation
changelog together. Breaking contracts need migration notes. Keep `uv.lock` and
`pnpm-lock.yaml` synchronized with dependency changes.

CI tests Python on Ubuntu and Windows, checks types/formatting, builds distributions,
checks their PyPI description and builds all sites. A successful push to `main`
publishes a version absent from PyPI and creates its GitHub release. The verified
site artifacts deploy to Cloudflare Workers from `main`.

Repository secrets:

- `PYPI_API_TOKEN`: scoped to the MLschema PyPI project.
- `CLOUDFLARE_API_TOKEN`: permission to deploy Workers and their custom domains.
- `CLOUDFLARE_ACCOUNT_ID`: the account containing the eshkra zone.

Domains are declared in each site's `wrangler.jsonc`. Docs, landing and playground
use `docs.mlschema.eshkra.dev`, `mlschema.eshkra.dev` and
`playground.mlschema.eshkra.dev`. A manual CI run on `main` can redeploy sites.

Publish MLschema 0.3.0 before updating downstream registry locks such as mlbundle's.
To verify the coordinated change before publication, install the local package
into the consumer environment with `uv pip install --python .venv --no-deps -e ../mlschema`
and run its checks with `uv run --no-sync`. This is a local test setup; refresh the
consumer's ordinary registry lock with `uv sync --all-extras` after publication.

Open focused pull requests describing the behavior change and actual verification.
Use Conventional Commit titles. Report security issues through the process in
[SECURITY.md](https://github.com/UlloaSP/mlschema/blob/main/SECURITY.md).
