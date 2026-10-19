# MLschema landing

The product site at <https://mlschema.eshkra.dev>, built with Astro. It shares the eshkra palette, Mona Sans and JetBrains Mono fonts, and the original MLschema mark from the repository's `brand/mlschema.png`. The page follows the visitor's light or dark system preference.

## Local development

Install once from the repository root, which owns the pnpm workspace and lockfile:

```sh
vp install --frozen-lockfile
```

Then, from this directory, with Node.js 22.18+, 24.11+, or 26+:

```sh
vp run dev
```

Open <http://127.0.0.1:4330>. `vp run build` checks Astro/TypeScript and produces the static site in `dist/`; `vp run preview` serves that build. Use `vp run check:format` to check formatting or `vp run format` to apply it.

## Examples are real output

Every example on the page lives in `examples/`. Running it with the MLschema checkout stores its schema (`<name>.json`) and its DataFrame columns, dtypes and first values, plus `feature_names` or `overrides` when the example defines them (`<name>.input.json`). The mapping diagrams are drawn from those files only: each field sits beside the column its `mappedTo` points to, and the build fails if a target has no column, a column has no field, or the shown call no longer appears in the example. A diagram shows `mappedTo` only where it differs from the label; the script and raw JSON, with every key, stay one click away, side by side. Regenerate the outputs in `src/data/examples/` after changing an example or the package:

```sh
vp run examples
```

`vp run check:examples` fails when a stored output is stale, or when `examples/kinds.py` no longer shows every builtin kind. Both commands use the repository's `uv` environment. The same run records the package's builtin kind order, which the page shows.

## Live MLform section

The integration section mounts the published `mlform` package on the hero example's real field list, prefilled with the first row of its DataFrame. The values pane shows MLform's own `createSubmissionSnapshot(form).modelValues`, so it is exactly what a transport would receive; the demo transport sends nothing. MLform and its runtime load only when the section approaches the viewport. If they fail to load, the section says so and points back to the example.

## Social card and version

`public/og.png` is a 1200×630 capture of this page's hero in light mode, with the navigation, actions and code stage hidden.

The latest version on PyPI is fetched once per build and shown beside the install command. When the request fails, the version is left out; none is invented.

## Deployment

`wrangler.jsonc` deploys `dist/` as static assets to the `mlschema.eshkra.dev` custom domain. Deploy from CI only.
