import type { PyodideAPI } from "pyodide";
import type { RunOutcome, RuntimeVersions } from "./protocol.ts";
import { PYODIDE_PACKAGES, PYPI_PINS, SOURCE_ROOT } from "./versions.ts";

export interface PythonSession {
  versions: RuntimeVersions;
  run(code: string): Promise<RunOutcome>;
}

/** Package-relative path, e.g. `mlschema/core/app/inference.py`, to file contents. */
export type SourceTree = Readonly<Record<string, string>>;

const writeSources = (pyodide: PyodideAPI, sources: SourceTree) => {
  const paths = Object.keys(sources);
  if (!paths.some((path) => path === "mlschema/__init__.py")) {
    throw new Error("The MLschema sources are missing from this build.");
  }
  for (const path of paths) {
    const target = `${SOURCE_ROOT}/${path}`;
    pyodide.FS.mkdirTree(target.slice(0, target.lastIndexOf("/")));
    pyodide.FS.writeFile(target, sources[path]!);
  }
};

/**
 * Prepare a loaded Pyodide instance: install the pinned wheels, write the real
 * MLschema sources and load the execution harness. Shared by the browser worker
 * and the Node runtime tests so both exercise the same path.
 */
export const startSession = async (
  pyodide: PyodideAPI,
  sources: SourceTree,
  harness: string,
  onProgress: (message: string) => void = () => {},
): Promise<PythonSession> => {
  onProgress("Loading pandas…");
  await pyodide.loadPackage([...PYODIDE_PACKAGES], { messageCallback: () => {} });
  onProgress("Installing pydantic…");
  const micropip = pyodide.pyimport("micropip");
  try {
    await micropip.install.callKwargs([...PYPI_PINS], { deps: false });
  } finally {
    micropip.destroy();
  }
  onProgress("Loading MLschema…");
  writeSources(pyodide, sources);
  const namespace = pyodide.toPy({});
  pyodide.runPython(harness, { globals: namespace, filename: "harness.py" });
  const versionsOf = namespace.get("runtime_versions");
  const runCode = namespace.get("run");
  const versions = JSON.parse(versionsOf(SOURCE_ROOT)) as RuntimeVersions;
  versionsOf.destroy();
  return {
    versions,
    async run(code) {
      return JSON.parse(await runCode(code)) as RunOutcome;
    },
  };
};
