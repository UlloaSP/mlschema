import assert from "node:assert/strict";
import { readdirSync } from "node:fs";
import { before, test } from "node:test";
import type { PythonSession } from "../../src/runtime/session.ts";
import { bootNodeSession, examplesDir, readExample } from "./load.ts";

type Field = Record<string, unknown> & { kind: string; mappedTo?: unknown };

let session: PythonSession;
before(async () => {
  session = await bootNodeSession();
});

const schemaOf = async (file: string): Promise<Field[]> => {
  const outcome = await session.run(readExample(file));
  assert.equal(outcome.kind, "json", JSON.stringify(outcome));
  return JSON.parse((outcome as { text: string }).text) as Field[];
};

test("the runtime matches the pinned interpreter and wheels", () => {
  assert.equal(session.versions.python.split(".").slice(0, 2).join("."), "3.14");
  assert.equal(session.versions.pydantic, "2.14.1");
  assert.match(session.versions.pandas, /^3\./);
});

test("every bundled example produces JSON", async () => {
  const files = readdirSync(examplesDir).filter((file) => file.endsWith(".py"));
  assert.equal(files.length, 7);
  for (const file of files) await schemaOf(file);
});

test("examples show the documented contract", async () => {
  const basic = await schemaOf("basic.py");
  assert.deepEqual(
    basic.map((field) => field.kind),
    ["text", "number", "number", "boolean", "date"],
  );
  assert.equal(basic[2]!.required, false);

  const categories = await schemaOf("categories.py");
  assert.deepEqual(
    categories.map((field) => field.kind),
    ["category", "onehot-category"],
  );

  const positional = await schemaOf("positional.py");
  const onehot = positional.find((field) => field.kind === "onehot-category")!;
  assert.deepEqual(
    (onehot.options as Field[]).map((option) => option.mappedTo),
    [0, 1],
  );
  assert.deepEqual(
    positional.filter((field) => field !== onehot).map((field) => field.mappedTo),
    [2, 3],
  );

  const custom = await schemaOf("custom_kind.py");
  assert.deepEqual(
    custom.map((field) => field.kind),
    ["number", "duration"],
  );

  const errors = await schemaOf("errors.py");
  assert.deepEqual(
    errors.map((entry) => entry.error),
    ["EmptyDataFrameError", "FieldBuilderError", "ValidationError"],
  );
});

test("series columns keep their own ids and mappings stay top level", async () => {
  const [reading] = await schemaOf("series.py");
  assert.equal(reading!.kind, "series");
  assert.equal(reading!.mappedTo, "reading");
  assert.equal(reading!.label, "Sensor reading");
  const columns = reading!.columns as Field[];
  assert.deepEqual(
    columns.map((column) => [column.id, column.kind, "mappedTo" in column]),
    [
      ["field1", "date", false],
      ["field2", "number", false],
    ],
  );
});

test("the harness reports values, errors and output faithfully", async () => {
  assert.deepEqual(await session.run("x = 1"), { kind: "none" });
  assert.deepEqual(await session.run("import asyncio\nawait asyncio.sleep(0)\n[1]"), {
    kind: "json",
    text: "[\n  1\n]",
  });
  assert.deepEqual(await session.run("import pandas as pd\npd.Series([1], name='a')"), {
    kind: "repr",
    typeName: "Series",
    text: "0    1\nName: a, dtype: int64",
  });
  const nan = await session.run("float('nan')");
  assert.equal(nan.kind, "repr", "NaN is not valid JSON");

  const syntax = await session.run("def broken(:\n    pass");
  assert.equal(syntax.kind, "error");
  assert.match((syntax as { text: string }).text, /File "<playground>", line 1[\s\S]*SyntaxError/);

  const raised = await session.run(
    "import pandas as pd\nfrom mlschema import infer_schema\ninfer_schema(pd.DataFrame())",
  );
  const text = (raised as { text: string }).text;
  assert.match(text, /^Traceback[\s\S]*File "<playground>", line 3/);
  assert.match(text, /mlschema\/core\/app\/inference\.py/);
  assert.match(text, /EmptyDataFrameError: DataFrame contains no columns or rows\.$/);
  assert.doesNotMatch(text, /harness\.py|_pyodide/, "harness frames are hidden");
});

test("each run starts from a fresh namespace", async () => {
  await session.run("leftover = 1");
  const outcome = await session.run("leftover");
  assert.equal(outcome.kind, "error");
  assert.match((outcome as { text: string }).text, /NameError/);
});
