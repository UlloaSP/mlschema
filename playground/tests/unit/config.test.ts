import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { PYODIDE_VERSION } from "../../src/runtime/versions.ts";
import { readWorkspaceState, saveWorkspaceState } from "../../src/workspace/state.ts";

const FALLBACK = { code: "x", exampleId: "basic", position: "left", ratio: 50 } as const;

test("the CDN loader version matches the installed pyodide package", () => {
  const installed = JSON.parse(
    readFileSync(new URL("../../node_modules/pyodide/package.json", import.meta.url), "utf8"),
  ) as { version: string };
  assert.equal(PYODIDE_VERSION, installed.version);
});

test("workspace state restores valid fields and falls back on invalid ones", () => {
  const storage = new Map<string, string>();
  const backend = {
    getItem: (key: string) => storage.get(key) ?? null,
    setItem: (key: string, value: string) => void storage.set(key, value),
  };
  assert.deepEqual(readWorkspaceState(backend, FALLBACK), FALLBACK);
  assert.equal(
    saveWorkspaceState(backend, { code: "y", exampleId: "series", position: "top", ratio: 95 }),
    true,
  );
  assert.deepEqual(readWorkspaceState(backend, FALLBACK), {
    code: "y",
    exampleId: "series",
    position: "top",
    ratio: 80,
  });
  storage.set([...storage.keys()][0]!, '{"position":"diagonal","ratio":"wide"}');
  assert.deepEqual(readWorkspaceState(backend, FALLBACK), FALLBACK);
  storage.set([...storage.keys()][0]!, "{not json");
  assert.deepEqual(readWorkspaceState(backend, FALLBACK), FALLBACK);
});

test("saving reports unavailable storage", () => {
  const full = {
    setItem() {
      throw new Error("QuotaExceededError");
    },
  };
  assert.equal(saveWorkspaceState(full, FALLBACK), false);
  assert.equal(saveWorkspaceState(undefined, FALLBACK), false);
});
