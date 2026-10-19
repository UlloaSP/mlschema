// Every snippet below is executed by scripts/examples.py; the JSON beside it is its real output,
// and each `.input.json` records the DataFrame (and options) that same run used.
import meta from "./examples/meta.json";

export type Json = null | boolean | number | string | Json[] | { [key: string]: Json };
export type Field = { [key: string]: Json };

export interface Column {
  // Unnamed (positional) DataFrame columns keep their integer label.
  name: string | number;
  dtype: string;
  values: string[];
}

export interface Example {
  file: string;
  code: string;
  output: string;
  schema: Field[];
  columns: Column[];
  featureNames?: string[];
  overrides?: Record<string, Field>;
}

const codes = import.meta.glob<string>("../../examples/*.py", {
  query: "?raw",
  import: "default",
  eager: true,
});
const outputs = import.meta.glob<string>("./examples/*.json", {
  query: "?raw",
  import: "default",
  eager: true,
});

const read = (name: string, suffix = "") => {
  const text = outputs[`./examples/${name}${suffix}.json`];
  if (text === undefined) throw new Error(`Run vp run examples: ${name}${suffix}.json is missing.`);
  return text;
};

export const example = (name: string): Example => {
  const code = codes[`../../examples/${name}.py`];
  if (code === undefined) throw new Error(`landing/examples/${name}.py does not exist.`);
  const output = read(name).trimEnd();
  return {
    file: `${name}.py`,
    code: code.trimEnd(),
    output,
    schema: JSON.parse(output),
    ...JSON.parse(read(name, ".input")),
  };
};

export const builtinKinds: string[] = meta.builtinKinds;
