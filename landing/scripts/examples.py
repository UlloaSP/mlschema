"""Run the landing examples against the local package and store their real output.

Every schema shown on the landing comes from executing `landing/examples/*.py`
with the MLschema checkout, and every diagram input comes from the same run's
DataFrame. `--check` fails when a stored output is stale.
"""

import json
import runpy
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

from mlschema.strategies.app import builtin_kinds

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"
OUTPUT = ROOT / "src" / "data" / "examples"
# The kinds example must keep showing every builtin kind the package resolves.
KINDS_EXAMPLE = "kinds"
INLINE_WIDTH = 72
# Example globals the diagrams use besides the DataFrame and its schema.
CONTEXT = {"feature_names": "featureNames", "overrides": "overrides"}
SAMPLES = 3


def render(value: Any, indent: int = 0) -> str:
    """Format JSON with two-space indents and short scalar lists on one line."""
    pad = " " * indent
    inner = " " * (indent + 2)
    if isinstance(value, dict) and value:
        items = (
            f"{inner}{json.dumps(key)}: {render(item, indent + 2)}"
            for key, item in value.items()
        )
        return "{\n" + ",\n".join(items) + f"\n{pad}}}"
    if isinstance(value, list) and value:
        flat = json.dumps(value, ensure_ascii=False)
        scalars = not any(isinstance(item, dict | list) for item in value)
        if scalars and len(flat) + indent <= INLINE_WIDTH:
            return flat
        items = (f"{inner}{render(item, indent + 2)}" for item in value)
        return "[\n" + ",\n".join(items) + f"\n{pad}]"
    return json.dumps(value, ensure_ascii=False)


def cell(value: Any) -> str:
    """Show a DataFrame cell the way the diagrams print it."""
    if isinstance(value, datetime):
        return value.isoformat(sep=" ").removesuffix(" 00:00:00")
    if isinstance(value, timedelta):
        return f"{value.total_seconds():g}s"
    if isinstance(value, tuple | list):
        return "(" + ", ".join(cell(item) for item in value) + ")"
    return str(value)


def frame(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Name, dtype and first values of every column, in DataFrame order."""
    return [
        {
            "name": name if isinstance(name, int) else str(name),
            "dtype": str(df[name].dtype),
            "values": [cell(value) for value in df[name].head(SAMPLES).tolist()],
        }
        for name in df.columns
    ]


def run_example(path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    scope = runpy.run_path(str(path))
    schema, df = scope.get("schema"), scope.get("df")
    if not isinstance(schema, list) or not isinstance(df, pd.DataFrame):
        raise SystemExit(
            f"{path.name} must define a DataFrame 'df' and a list 'schema'."
        )
    inputs = {"columns": frame(df)}
    inputs |= {key: scope[name] for name, key in CONTEXT.items() if name in scope}
    return schema, inputs


def package_meta(kinds_schema: list[dict[str, Any]]) -> dict[str, Any]:
    builtin = [item.name for item in builtin_kinds()]
    shown = {field["kind"] for field in kinds_schema}
    if shown != set(builtin):
        raise SystemExit(
            f"{KINDS_EXAMPLE}.py shows {sorted(shown)}; builtin kinds are {builtin}."
        )
    return {
        "builtinKinds": builtin,
    }


def outputs() -> dict[Path, str]:
    runs = {path.stem: run_example(path) for path in sorted(EXAMPLES.glob("*.py"))}
    files: dict[Path, str] = {}
    for name, (schema, inputs) in runs.items():
        files[OUTPUT / f"{name}.json"] = render(schema)
        files[OUTPUT / f"{name}.input.json"] = render(inputs)
    files[OUTPUT / "meta.json"] = render(package_meta(runs[KINDS_EXAMPLE][0]))
    return {path: text + "\n" for path, text in files.items()}


def main(check: bool) -> None:
    expected = outputs()
    if check:
        stale = sorted(
            path.name
            for path, text in expected.items()
            if not path.is_file() or path.read_text(encoding="utf-8") != text
        )
        if stale:
            raise SystemExit(f"Stale landing examples: {', '.join(stale)}.")
        return
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for path in OUTPUT.glob("*.json"):
        if path not in expected:
            path.unlink()
    for path, text in expected.items():
        path.write_text(text, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main(check="--check" in sys.argv[1:])
