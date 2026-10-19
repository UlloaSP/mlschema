import type { SourceTree } from "./session.ts";

// The repository's real package source, bundled at build time. Never a copy.
const files = import.meta.glob<string>("../../../src/mlschema/**/*.py", {
  query: "?raw",
  import: "default",
  eager: true,
});

export const MLSCHEMA_SOURCES: SourceTree = Object.fromEntries(
  Object.entries(files).map(([path, text]) => [path.slice(path.indexOf("mlschema/")), text]),
);
