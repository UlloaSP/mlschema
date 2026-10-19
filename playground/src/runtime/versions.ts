// Pinned so every visitor gets the same interpreter and wheels.
export const PYODIDE_VERSION = "314.0.7";
export const PYODIDE_INDEX_URL = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;

// Wheels shipped with this Pyodide release. Its pandas (3.0.2) is one patch below
// MLschema's declared minimum; no newer pandas wheel exists for this ABI.
export const PYODIDE_PACKAGES = ["micropip", "pandas"] as const;

// Pyodide ships pydantic 2.12.5, below MLschema's minimum. These exact wheels come
// from PyPI; pydantic-core publishes a pyemscripten_2026_0 build for this ABI.
export const PYPI_PINS = [
  "pydantic==2.14.1",
  "pydantic-core==2.50.1",
  "typing-extensions==4.16.0",
  "typing-inspection==0.4.4",
  "annotated-types==0.7.0",
] as const;

// Where the repository's src/ tree is written inside the Pyodide file system.
export const SOURCE_ROOT = "/mlschema/src";

export const BOOT_TIMEOUT_MS = 180_000;
export const RUN_TIMEOUT_MS = 15_000;
export const OUTPUT_LIMIT_CHARS = 100_000;
