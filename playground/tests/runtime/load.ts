import { readFileSync, readdirSync } from "node:fs";
import { join, relative } from "node:path";
import { fileURLToPath } from "node:url";
import { loadPyodide } from "pyodide";
import { startSession, type PythonSession, type SourceTree } from "../../src/runtime/session.ts";

const here = fileURLToPath(new URL(".", import.meta.url));
export const repoRoot = join(here, "../../..");
export const examplesDir = join(here, "../../src/examples");

const pythonFiles = (dir: string): string[] =>
  readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) return pythonFiles(path);
    return entry.name.endsWith(".py") ? [path] : [];
  });

/** Same tree the Vite build bundles: every .py file under src/mlschema. */
export const readSources = (): SourceTree => {
  const srcRoot = join(repoRoot, "src");
  return Object.fromEntries(
    pythonFiles(join(srcRoot, "mlschema")).map((path) => [
      relative(srcRoot, path).replaceAll("\\", "/"),
      readFileSync(path, "utf8"),
    ]),
  );
};

export const harnessSource = () =>
  readFileSync(join(here, "../../src/runtime/harness.py"), "utf8");
export const readExample = (file: string) => readFileSync(join(examplesDir, file), "utf8");

/** Boots real Pyodide with the pinned wheels; downloads from jsDelivr and PyPI. */
export const bootNodeSession = async (): Promise<PythonSession> => {
  const pyodide = await loadPyodide({ stdout: () => {}, stderr: () => {} });
  return startSession(pyodide, readSources(), harnessSource());
};
