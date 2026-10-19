// Mapping diagrams: each DataFrame column beside the field that claims it, from real example runs.
import { example, type Column, type Example, type Field, type Json } from "./examples";

export interface Source extends Column {
  // Position in the model's feature vector, when the example converts to positional targets.
  slot?: number;
}

export interface Row {
  columns: Source[];
  field: Field;
  // Keys the example set by hand through overrides; the diagram marks them.
  changed: string[];
}

export interface Diagram {
  id: string;
  title: string;
  call: string;
  // One line on what this example shows, under the call.
  note?: string;
  example: Example;
  rows: Row[];
}

const isField = (value: Json | undefined): value is Field =>
  typeof value === "object" && value !== null && !Array.isArray(value);

// A field maps through its own mappedTo; a one-hot field maps through each option instead.
const targets = (field: Field): Json[] => {
  if ("mappedTo" in field) return [field.mappedTo!];
  const options = Array.isArray(field.options) ? field.options : [];
  return options
    .filter(isField)
    .flatMap((option) => ("mappedTo" in option ? [option.mappedTo!] : []));
};

const diagram = (id: string, title: string, call: string, note?: string): Diagram => {
  const source = example(id);
  const { columns, featureNames, overrides = {} } = source;
  if (!source.code.includes(call)) throw new Error(`${source.file} no longer calls ${call}.`);
  const used = new Set<Column>();
  // Integer targets index the model's feature names when the example has them, else the frame.
  const resolve = (target: Json): Source => {
    const name = typeof target === "number" && featureNames ? featureNames[target] : target;
    const column = columns.find((item) => item.name === name);
    if (!column)
      throw new Error(`${source.file}: mappedTo ${JSON.stringify(target)} has no column.`);
    used.add(column);
    const slot = featureNames?.indexOf(String(column.name));
    return slot === undefined ? column : { ...column, slot };
  };
  const rows = source.schema.map((field) => {
    const sources = targets(field).map(resolve);
    const changed = sources.flatMap(({ name }) => Object.keys(overrides[String(name)] ?? {}));
    return { columns: sources, field, changed };
  });
  if (used.size !== columns.length) throw new Error(`${source.file}: a column has no field.`);
  return { id, title, call, note, example: source, rows };
};

export const hero = diagram("hero", "hero.py", "infer_schema(df)");
export const kinds = diagram("kinds", "kinds.py", "infer_schema(df)");
export const mapping = [
  diagram(
    "model_order",
    "Model order",
    "with_positional_mappings(infer_schema(df), feature_names)",
    "feature_names is the order the model was trained with. Unknown or duplicate names raise ValueError.",
  ),
  diagram(
    "positional",
    "Unnamed columns",
    "infer_schema(df)",
    "Columns without names get feature_0, feature_1… as labels and their positions as targets.",
  ),
];
export const refine = [
  diagram(
    "overrides",
    "overrides",
    "infer_schema(df, overrides=overrides)",
    "Patch labels, bounds, defaults or units after inference.",
  ),
  diagram(
    "builder",
    "builders",
    "infer_schema(df, builders=[money_builder])",
    "Claim a column with an existing kind and add your own metadata.",
  ),
  diagram(
    "kind",
    "custom kinds",
    "infer_schema(df, kinds=[kind(model=DurationField, infer=duration_builder)])",
    "Register a new kind with its own Pydantic model.",
  ),
];
