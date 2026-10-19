# MLschema

MLschema is a Python library that derives validated field schemas from pandas DataFrames.

Columns, dtypes and values provide the initial contract. Builders infer fields, overrides refine them, and strict Pydantic models validate the result. The output is a JSON-compatible field list that applications can pass to MLform, include in MLbundle, or consume independently.

Read this root file first, then the nearest nested `AGENTS.md` for the area being changed. Nested instructions take precedence within their subtree.

## What must remain true

### 1. Inference and validation share one contract

The field models own validation and serialization. Builders propose field dictionaries; they do not establish a parallel definition of valid fields.

Keep inference rules in their owning Python modules. Websites, examples and downstream consumers use the resulting contract rather than reconstructing it.

### 2. Backend identity is explicit

Column names, display labels and backend `mappedTo` targets serve different purposes.

Named DataFrame columns map to their names. Columns forming the positional sequence `0..n-1` map to integer positions and receive generated labels. Changing a label does not implicitly change its target.

One-hot fields map through `options[].mappedTo`; their parent has no `mappedTo`. Series fields map at the parent; their ordered `columns[]` use local ids and scalar-kind validation, without backend mappings.

Use `with_positional_mappings()` for explicit conversion into a model's feature order. It returns a copy and rejects missing, unknown or ambiguous targets instead of guessing from labels.

### 3. Extensions follow the normal path

Custom builders and custom kinds use the same inference context, validation and serialization as built-ins.

Builder order is observable behavior: user builders precede custom-kind builders and built-ins; the first non-`None` result wins. The text builder is the final fallback. Named one-hot groups are handled by the inference pipeline before ordinary columns.

Keep overrides in the validation path. A patch that violates the selected field model must fail rather than bypass its constraints.

### 4. The library owns field inference

MLschema produces a field list, not a complete frontend application or a JSON Schema document. Rendering, reports, transport, model execution and application-specific rules belong to consumers.

MLform compatibility is an output contract, not a dependency on a browser or a rendering runtime. The Python package must remain usable independently of the product websites.

### 5. Examples describe actual behavior

Published examples and diagrams must agree with the current Python implementation. Generate example data through the library and verify it before presenting it as output.

Supported environments come from `pyproject.toml` and verification. The playground's experimental Pyodide environment does not establish support for a different desktop dependency range.

## Maintainer intent

Favor small, explicit models that support useful capabilities without parallel rules.

Remove complexity whose original constraint no longer exists. Compatibility paths, migration fields and configuration need a current purpose.

Implement the smallest coherent change that fixes the owning rule and every affected path. Preserve data compatibility unless the task explicitly permits a breaking change.

These instructions are defaults unless marked as invariants. An explicit maintainer request may override a default. Explain conflicts with an invariant or public contract before proceeding.

Use the `caveman` skill in ultra mode for user communication. Keep product copy and repository documentation in English.

## Vocabulary

- **field list / schema**: the ordered JSON-compatible dictionaries returned by inference
- **field**: a validated input description, including its kind and external mapping
- **builder**: callable receiving a pandas Series and `FieldContext`, returning a field dictionary or `None`
- **kind**: a discriminator paired with a strict field model and inference builder
- **context**: column metadata and the callback used for nested field inference
- **override**: a column-keyed patch applied after ordinary field inference and before validation
- **mapped target**: external feature identity expressed through `mappedTo`
- **series column**: a local scalar field description inside an ordered `columns[]` list
- **positional conversion**: explicit rewriting of targets against an ordered feature-name list

## Invariants

- Source files stay at or below 300 lines. Split by responsibility before crossing the limit.
- Python environments and commands use `uv`; linting/formatting use Ruff and type checking uses Pyright.
- Product-site workspace tasks use Vite+ (`vp`). Python packaging remains separate from the pnpm workspace.
- The supported public API is exported from `mlschema`; public exceptions are exported from `mlschema.core`. Internal implementation paths remain private.
- Public API and schema changes are deliberate and visible, with corresponding examples, tests and documentation.
- Rules have one owner. Duplication requires an explicit UX or runtime reason.
- New runtime dependencies require a concrete benefit that existing code, platform APIs or current dependencies cannot provide cleanly.
- Verification claims match commands actually run. Unsupported environments and known limits remain explicit.
- Brand spelling is `MLschema`. Package names, imports, URLs, paths and technical identifiers retain their actual spelling.

## How MLschema fits together

Typical flow:

1. Validate the DataFrame input and derive column labels and mapped targets.
2. Assemble active kind models and ordered builders; identify named one-hot groups.
3. Build column context and run builders until one claims an ordinary column.
4. Apply matching overrides and validate through the selected field model.
5. Serialize fields in JSON mode, preserving field order and one-hot grouping.
6. Optionally convert named mappings to a consumer's ordered input positions.

Complexity belongs at the inference, dtype, field-validation and mapping boundaries. A caller should not need to repair the schema shape after inference.

## Where code lives

- `src/mlschema/core/app` — inference, extension contracts and positional mapping conversion
- `src/mlschema/core/domain` — shared strict field contract
- `src/mlschema/core/exceptions` — public inference errors
- `src/mlschema/core/util` — dtype normalization
- `src/mlschema/strategies/app` — built-in builders and their order
- `src/mlschema/strategies/domain` — built-in field models and series-column validation
- `test/unit`, `test/integration`, `test/architecture`, `test/load` — focused behavior, workflows, boundaries and scale
- `docs` — Astro Starlight documentation
- `landing` — product site and executable examples
- `playground` — browser editor and experimental Python worker
- `brand` — shared product assets

Treat `pyproject.toml`, package scripts, module exports and tests as the source of truth for versions, commands and public structure. A generated relationship graph, when present, can help broad navigation; it is not required to understand a focused change.

## Check every affected path

Apply the entries relevant to the change:

- **Inference:** builder precedence, first-match behavior, dtype handling and fallback remain intentional.
- **Identity:** named targets, positional targets, display labels and one-hot option targets stay distinct.
- **Validation:** built-in and custom fields, overrides and nested series columns obey their owning models.
- **Mapping:** conversion preserves the original input, field grouping and nested values; invalid targets fail explicitly.
- **Extensions:** custom builders and kinds use the same success and error paths as built-ins.
- **Errors:** exception type, context and validation diagnostics still describe the failure.
- **Consumers:** Python output, MLform-compatible fields and downstream adapters agree on one shape.
- **Packaging:** exports, typing markers, dependency bounds and built distributions remain usable independently of the sites.
- **Sites:** Python examples, displayed output, keyboard behavior and browser-worker lifecycle match the documented capability.

A change is incomplete when it works only through the path used by its first test.

## Change style

Fix root causes at their owning boundary. Prefer an existing abstraction over a parallel one, explicit contracts over fallback guesses, and deletion over unused compatibility scaffolding.

Keep comments focused on reasons that the code cannot express. Remove dead branches, placeholder implementations and flags without a complete supported path.

When a file mixes responsibilities or approaches 300 lines, split around ownership rather than extracting arbitrary helpers. Keep package `__init__.py` files focused on public exports.

For non-trivial work, establish scope and verification before editing. Delegate independent work when useful and keep shared-file ownership explicit. User-interface implementation belongs to Claude Opus 5.5 with high effort when that provider is available; report a missing capability instead of silently substituting another model.

## Compatibility

MLschema is pre-1.0. Preserve an existing contract when the task requires compatibility. When a clean break is intended, remove the old implementation, tests, examples, documentation and migration-only fallbacks together.

Document changes to field shapes and mappings in the upgrade notes. Downstream packages should consume the library's contract instead of retaining patches for behavior now owned here.

## Testing

Use the smallest proof that exercises observable behavior:

- Start with the focused test file or affected group.
- Put new tests for one feature in one focused file, covering success and each affected error case.
- Test public results and failures rather than private wiring.
- Use integration tests when correctness depends on multiple modules or a complete field-list workflow.
- Use browser-backed verification for rendering, focus, keyboard interaction and real worker behavior.
- Wait for observable events or state transitions instead of arbitrary sleeps.

For Python source or public-contract changes, the usual quality gates are:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
uv build
```

For sites, use the affected package's declared checks and `vp run build` when all sites are affected. Validate landing examples with `uv run python landing/scripts/examples.py --check` when their code or displayed output changes.

A documentation-only edit needs relevant example, link and rendering checks, not every code gate. A README used as the PyPI description must remain valid distribution metadata.

If verification cannot run, report the exact command, failure and unverified scope.

## Documentation and product sites

Explain what a capability does, how to use it, its external contract and non-obvious limits. Keep architecture guidance focused on durable decisions and traps rather than implementation inventories or task history.

Rewrite or remove stale guidance when behavior changes. Record known limitations alongside the affected capability, with a clear distinction between current behavior and intended work.

Keep `README.md` focused on identity, installation, primary usage, customization and links to detailed docs. Its content serves both GitHub and PyPI; use links and assets that work in both contexts.

Use shared eshkra assets and the `MLschema` wordmark. Landing examples should explain distinct benefits without repeating code-shaped diagrams. Paired input/output examples stay side by side at every breakpoint, with contained horizontal navigation where necessary. Verify mobile and desktop, light and dark, and keyboard operation for changed interactions.

When asked to run local sites, leave the verified servers running and report their URLs. Keep experimental runtime details accurate in the playground documentation.

## Git and pull requests

Preserve unrelated working-tree changes, including intentional deletions. Do not recreate removed plans, caches or generated artifacts merely because an old instruction referenced them.

Commit, push, create branches and open pull requests only when requested. Use Conventional Commit titles and keep each change focused.

Keep transient plans, scratch notes, browser artifacts, generated coverage and review-only evidence out of commits. Pull request descriptions explain the resulting behavior and actual verification.

## Done

Work is complete when the requested behavior works through every affected path, the owning layer contains the rule, public contracts remain intentional, stale guidance is gone, relevant verification has run, and the result is simpler or more explicit than before.
