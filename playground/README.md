# MLschema playground

Write Python on the left and see the schema it produces as JSON on the right. Part of [eshkra](https://eshkra.dev).

Public site: <https://playground.mlschema.eshkra.dev/>. Documentation: <https://docs.mlschema.eshkra.dev/>.

## How it runs

Python runs in your browser on [Pyodide](https://pyodide.org/), inside a dedicated Web Worker. Nothing executes on a server and your code is never uploaded.

- The playground does not install the `mlschema` package from PyPI. The build bundles every `.py` file from this repository's `src/mlschema` into the worker, which writes them into Pyodide's file system and imports them. The page therefore always runs the source it was built from.
- The worker has no access to the page, its DOM or its storage. A run that exceeds 15 seconds, or that you stop, terminates the worker; a fresh Python starts and variables and imports are reset. **Restart Python** does the same on request.
- Each run executes in a fresh namespace. The value of the last expression is shown as JSON; values that are not valid JSON, such as a DataFrame or `NaN`, are shown with `repr()`. `print()` output and stderr appear under **Console**, capped at 100,000 characters per run. Exceptions show their traceback from your code into MLschema.
- Top-level `await` works. Ctrl/⌘ + Enter runs the code. Tab indents; press Escape, then Tab, to leave the editor.
- The selected example, your code and the panel layout are saved in this browser. **Reset example** restores the example.

## Interface

The page follows the MLForm playground. The header holds the MLschema brand and icon links to the documentation, GitHub and eshkra. Every icon-only control (reset, restart, run/stop, status, copy) names itself in a tooltip on hover and on keyboard focus, and keeps that name as its accessible name. Copy floats over the JSON result and appears only while there is JSON to copy.

The floating options menu at the top left opens with a click or with Arrow Down, and closes with Escape, a click outside it, or a click into the editor. Its only workspace is **Code › Editor**. Its settings:

- **Design system**: MLForm's themes (eshkra, M3DISEEN, DoseTailor, ClickHouse, Airbnb, Neutral, Cobalt, Sage, Sunset, Graphite). The playground copies their colors and radii into CSS; it keeps its own fonts and loads no MLForm code.
- **Style**: MLForm's recipes. Minimal is compact with no motion or shadows, Soft tints the toolbar and menu, Contrast draws heavier borders in the text colour.
- **Appearance**: System, Light or Dark.
- **Viewport size**: the current window, a device preset (phone, tablet, laptop, PC, ultrawide) or a custom size from 1 to 8192 px. A simulated viewport shrinks to fit the window width and may scroll vertically.

The workspace lives in one same-origin frame (`?editor=1`) that stays loaded: changing the viewport resizes or scales that frame, so the code, the result and the running Python are kept. Settings are saved in this browser under `mlschema-playground-settings`; an invalid saved value falls back to its default without resetting the others.

## Experimental runtime

This is not an officially supported MLschema environment. MLschema declares Python 3.14, `pandas>=3.0.3,<4.0.0` and `pydantic>=2.13.4,<3.0.0`. The playground pins:

| Component | Version | Source |
| --- | --- | --- |
| Pyodide | 314.0.7 (Python 3.14.2) | jsDelivr CDN |
| pandas, numpy | 3.0.2, 2.4.6 | Pyodide distribution |
| pydantic, pydantic-core | 2.14.1, 2.50.1 | PyPI |
| typing-extensions, typing-inspection, annotated-types | 4.16.0, 0.4.4, 0.7.0 | PyPI or Pyodide |

pandas 3.0.2 is one patch below MLschema's minimum. No newer pandas wheel exists for Pyodide's `pyemscripten_2026_0` ABI: the pandas wheels for WebAssembly on PyPI target the older `pyemscripten_2024_0` ABI and Python 3.12. Pyodide's own pydantic (2.12.5) is below the minimum, so the worker installs exact pydantic wheels from PyPI instead; pydantic-core publishes a WebAssembly build for this ABI. The package's supported floor is unchanged.

`test:runtime` runs the repository's full pytest suite inside this runtime, so an incompatibility shows up as a failing test. These limitations are documented here and in `tasks/debt.md`; the page itself shows no runtime notice.

The first visit downloads Python, pandas and pydantic from `cdn.jsdelivr.net`, `pypi.org` and `files.pythonhosted.org`; later visits use the browser cache. If those hosts are blocked or offline, the page reports that Python could not start and offers **Restart Python**.

To move to a new Pyodide release, update `pyodide` in `package.json` and `PYODIDE_VERSION` in `src/runtime/versions.ts` together (a unit test checks they match), then review `PYPI_PINS` against the release's `pyodide-lock.json` and PyPI.

## Examples

`src/examples/*.py` are ordinary Python files: basic fields, overrides, categories and one-hot groups, series columns, positional mappings with `with_positional_mappings`, a custom builder and kind, and error handling. Each ends with the expression the playground displays. `src/examples/ruff.toml` relaxes the lint rules that conflict with that style. `test:runtime` runs every example against the real package.

## Commands

From this directory, after `vp install --frozen-lockfile` at the repository root:

```bash
vp run dev          # http://127.0.0.1:10011
vp run build
vp run preview
vp run typecheck
vp run test:unit    # runtime client, configuration, saved workspace and settings
vp run test:runtime # real Pyodide in Node: examples, harness and the pytest suite
vp run test:e2e     # production build in Chromium, desktop and mobile: runtime, controls, menu, viewport
```

`test:runtime` and `test:e2e` download Pyodide and wheels, so they need network access. Before the first `test:e2e`, run `vp exec playwright install chromium`.

## Hosting

`wrangler.jsonc` serves `dist/` as static assets on Cloudflare Workers at `playground.mlschema.eshkra.dev`, with no Worker script. The custom domain creates its DNS record and certificate on deploy. `public/_headers` sets basic security headers and long caching for hashed assets. Deploy only from CI.
