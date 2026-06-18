# Technical Debt

- Reports/explanations domain leak removed from active code/docs/tests.
- Legacy class/registry strategy API removed from active code/docs/tests; public API is now `infer_schema()`.
- Builtin inference and strict exception modules are split by responsibility.
- Tests are modularized by scope: unit, integration, architecture, and load.
- Oversized tracked test/docs files were replaced with smaller focused files; only ignored generated cache artifacts remain above the line guideline.
- Active schema contract now emits explicit `mappedTo` targets for normal fields and `options[].mappedTo` for `onehot-category`; named encoded feature columns can group into onehot categories, while positional columns stay ordinary fields with generated `feature_<position>` labels and integer targets.
