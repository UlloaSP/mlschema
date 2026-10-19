---
title: MLschema documentation
description: Infer validated, frontend-ready field schemas from pandas DataFrames, then refine only what is product-specific.
tableOfContents: false
hero:
  title: Typed inputs, straight from your data.
  tagline: MLschema reads a pandas DataFrame and returns a validated, JSON-serialisable list of fields. Each field carries a kind, a label, nullability and the backend target the model expects.
  actions:
    - text: Quick start
      link: /getting-started/quick-start/
      variant: primary
    - text: The field contract
      link: /schema/overview/
      variant: secondary
    - text: Open the playground
      link: https://playground.mlschema.eshkra.dev/
      variant: minimal
      icon: external
---

```python title="schema.py"
import pandas as pd

from mlschema import infer_schema

df = pd.DataFrame(
    {
        "score": [98.5, 86.0, 91.0],
        "role": pd.Categorical(["engineer", "engineer", "scientist"]),
        "active": [True, False, True],
    }
)

fields = infer_schema(df)
```

```json title="fields"
[
  { "label": "score", "required": true, "mappedTo": "score", "kind": "number", "step": 0.1 },
  {
    "label": "role",
    "required": true,
    "mappedTo": "role",
    "kind": "category",
    "options": ["engineer", "scientist"]
  },
  { "label": "active", "required": true, "mappedTo": "active", "kind": "boolean" }
]
```

Every field is checked against a strict Pydantic model before it is returned. Constraints that
contradict each other, unknown attributes and unknown kinds fail during inference instead of
reaching your interface.

## Find your path

<div class="path-grid not-content">
  <a class="path-card" href="/getting-started/quick-start/">
    <strong>Infer a first schema</strong>
    <span>Shape a DataFrame, call <code>infer_schema</code>, and read the result.</span>
  </a>
  <a class="path-card" href="/schema/field-kinds/">
    <strong>Know the field kinds</strong>
    <span>Seven built-in kinds, how each is detected, and what it accepts.</span>
  </a>
  <a class="path-card" href="/schema/mappings/">
    <strong>Reach the model</strong>
    <span><code>mappedTo</code> targets, one-hot groups, and positional feature vectors.</span>
  </a>
  <a class="path-card" href="/guides/overrides/">
    <strong>Refine the result</strong>
    <span>Labels, bounds, defaults and units, validated with the rest.</span>
  </a>
  <a class="path-card" href="/guides/extensions/">
    <strong>Add your own rules</strong>
    <span>Builders for existing kinds and <code>kind()</code> for new ones.</span>
  </a>
  <a class="path-card" href="/guides/mlform/">
    <strong>Render a form</strong>
    <span>Pass the fields to MLForm and submit the values the model expects.</span>
  </a>
</div>

MLschema is open source under the MIT license and part of [eshkra](https://eshkra.dev). Install it
from [PyPI](https://pypi.org/project/mlschema/), try it in the
[playground](https://playground.mlschema.eshkra.dev/), or read the source on
[GitHub](https://github.com/UlloaSP/mlschema).
