const docs = "https://docs.mlschema.eshkra.dev/";
const playground = "https://playground.mlschema.eshkra.dev/";
const github = "https://github.com/UlloaSP/mlschema";

export const links = {
  home: "https://mlschema.eshkra.dev/",
  eshkra: "https://eshkra.dev/",
  docs,
  playground,
  github,
  issues: `${github}/issues`,
  changelog: `${github}/releases`,
  license: `${github}/blob/main/LICENSE`,
  pypi: "https://pypi.org/project/mlschema/",
  mlform: "https://mlform.eshkra.dev/",
  quickStart: `${docs}getting-started/quick-start/`,
  mlformGuide: `${docs}guides/mlform/`,
  errors: `${docs}guides/errors/`,
};

export const install = "pip install mlschema";

export const description =
  "Infer validated, JSON-serialisable field schemas from pandas DataFrames. Seven builtin kinds, explicit backend mappings, overrides, custom builders and custom kinds.";

// The eshkra path from a trained model to a reviewed prediction, as on eshkra.dev.
export const family = [
  { name: "mlbundle", stage: "Package", href: "https://github.com/UlloaSP/mlbundle" },
  { name: "mlschema", stage: "Describe", href: "https://mlschema.eshkra.dev/" },
  { name: "mlform", stage: "Render", href: "https://mlform.eshkra.dev/" },
  { name: "mlsuite", stage: "Run & review", href: "https://github.com/UlloaSP/mlsuite" },
] as const;
