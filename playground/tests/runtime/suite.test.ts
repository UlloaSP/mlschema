import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { join, relative } from "node:path";
import { test } from "node:test";
import { loadPyodide } from "pyodide";
import { startSession } from "../../src/runtime/session.ts";
import { harnessSource, readSources, repoRoot } from "./load.ts";

const testFiles = (dir: string): string[] =>
  readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) return entry.name === "__pycache__" ? [] : testFiles(path);
    return entry.name.endsWith(".py") ? [path] : [];
  });

// The playground runs pandas and pydantic builds that differ from the supported
// environment, so the repository's own test suite must pass inside it.
test("the repository pytest suite passes in the playground runtime", async () => {
  let output = "";
  const pyodide = await loadPyodide({
    stdout: (line) => void (output += `${line}\n`),
    stderr: (line) => void (output += `${line}\n`),
  });
  await startSession(pyodide, readSources(), harnessSource());
  await pyodide.loadPackage(["pytest", "packaging"], { messageCallback: () => {} });
  await pyodide.pyimport("micropip").install("pytest-mock==3.15.1");
  for (const file of [...testFiles(join(repoRoot, "test")), join(repoRoot, "pyproject.toml")]) {
    const target = `/mlschema/${relative(repoRoot, file).replaceAll("\\", "/")}`;
    pyodide.FS.mkdirTree(target.slice(0, target.lastIndexOf("/")));
    pyodide.FS.writeFile(target, readFileSync(file, "utf8"));
  }
  const code = pyodide.runPython(
    'import os, pytest\nos.chdir("/mlschema")\nint(pytest.main(["-q", "-p", "no:cacheprovider"]))',
  ) as number;
  assert.equal(code, 0, output);
  assert.match(output, /\d+ passed/);
});
