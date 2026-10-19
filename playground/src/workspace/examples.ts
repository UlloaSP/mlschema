const sources = import.meta.glob<string>("../examples/*.py", {
  query: "?raw",
  import: "default",
  eager: true,
});

export interface CodeExample {
  id: string;
  label: string;
  code: string;
}

const CATALOG = [
  ["basic", "Basic fields"],
  ["overrides", "Overrides"],
  ["categories", "Categories and one-hot"],
  ["series", "Series columns"],
  ["positional", "Positional mappings"],
  ["custom_kind", "Custom builder and kind"],
  ["errors", "Handling errors"],
] as const;

export const CODE_EXAMPLES: readonly CodeExample[] = CATALOG.map(([id, label]) => {
  const code = sources[`../examples/${id}.py`];
  if (code === undefined) throw new Error(`Missing example file: ${id}.py`);
  return { id, label, code };
});

export const getCodeExample = (id: unknown): CodeExample =>
  CODE_EXAMPLES.find((example) => example.id === id) ?? CODE_EXAMPLES[0]!;
