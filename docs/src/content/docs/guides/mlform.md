---
title: Use with MLForm
description: Serve the inferred fields to MLForm and receive the values your model expects.
---

[MLForm](https://docs.mlform.eshkra.dev/) renders schema-driven forms in the browser and submits
each value under its field's `mappedTo`. MLschema produces the `fields` half of an MLForm schema.

## Serve the fields

```python
import pandas as pd

from mlschema import infer_schema

training = pd.read_parquet("training.parquet")
features = training.drop(columns=["target"])

fields = infer_schema(
    features,
    overrides={"age": {"label": "Age", "min": 0, "max": 120, "unit": "years"}},
)
```

Return `fields` from an endpoint in your web framework. Reports, layout, and ids are frontend
concerns, so the frontend adds them:

```ts title="main.ts"
import { mountForm } from "mlform";

const fields = await (await fetch("/api/schema")).json();

mountForm(document.querySelector<HTMLElement>("#form")!, {
  schema: {
    fields,
    reports: [{ id: "prediction", kind: "regressor", label: "Prediction", mappedTo: "prediction" }],
  },
  transport: {
    async submit(request) {
      const response = await fetch("/api/predict", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(request.modelValues),
        signal: request.signal,
      });
      if (!response.ok) throw new Error(`Prediction failed: ${response.status}`);
      return response.json();
    },
  },
});
```

MLForm generates a field id from each `label` when none is given. Add explicit `id` values on the
frontend, or through overrides, when your code, layout, or tests refer to fields.

## What the model receives

`request.modelValues` is keyed by `mappedTo`:

- a named field sends its value under the column name, such as `{ "age": 42 }`;
- an `onehot-category` field sends `1` for the selected option's column and `0` for the others;
- a `series` field sends its rows under the series target, each row keyed by `field1` and `field2`.

Positional targets from [`with_positional_mappings`](/schema/mappings/#models-that-take-a-feature-vector)
are sent as the keys `"0"`, `"1"`, and so on. MLForm does not build arrays, so the backend or
transport orders the values into the model's feature vector.

## Validate on both sides

MLschema validates fields when they are inferred. MLForm validates the whole schema again when it
mounts, against its own registry, and rejects kinds it does not know. A
[custom kind](/guides/extensions/#custom-kinds) needs a matching
[MLForm field definition](https://docs.mlform.eshkra.dev/extend/custom-fields/). To check a served
schema without mounting a form, use
[`validateSchema`](https://docs.mlform.eshkra.dev/schema/overview/#schemas-from-a-backend).
