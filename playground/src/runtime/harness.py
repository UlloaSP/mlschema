"""Execution harness for the MLschema playground. Runs inside Pyodide only."""

import json
import linecache
import sys
import traceback
from importlib import import_module
from types import TracebackType

# This module exists only in the Pyodide runtime exercised by test:runtime.
from pyodide.code import eval_code_async  # pyright: ignore[reportMissingImports]

FILENAME = "<playground>"


def runtime_versions(source_root: str) -> str:
    """Put the repository sources first on sys.path and report runtime versions."""
    if source_root not in sys.path:
        sys.path.insert(0, source_root)
    import numpy  # noqa: PLC0415
    import pandas  # noqa: PLC0415
    import pydantic  # noqa: PLC0415

    import_module("mlschema")

    return json.dumps(
        {
            "python": sys.version.split()[0],
            "pandas": pandas.__version__,
            "pydantic": pydantic.VERSION,
            "numpy": numpy.__version__,
        }
    )


def _user_traceback(error: BaseException) -> TracebackType | None:
    tb = error.__traceback__
    while tb is not None and tb.tb_frame.f_code.co_filename != FILENAME:
        tb = tb.tb_next
    return tb


def _format_error(error: BaseException) -> str:
    lines = traceback.format_exception(type(error), error, _user_traceback(error))
    return "".join(lines).rstrip()


async def run(code: str) -> str:
    """Run code in a fresh namespace and describe its last expression as JSON."""
    linecache.cache[FILENAME] = (len(code), None, code.splitlines(True), FILENAME)
    namespace = {"__name__": "__main__"}
    try:
        value = await eval_code_async(code, namespace, filename=FILENAME)
    except BaseException as error:
        return json.dumps({"kind": "error", "text": _format_error(error)})
    finally:
        sys.stdout.flush()
        sys.stderr.flush()
    if value is None:
        return json.dumps({"kind": "none"})
    try:
        text = json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)
    except TypeError, ValueError:
        return json.dumps(
            {"kind": "repr", "typeName": type(value).__qualname__, "text": repr(value)}
        )
    return json.dumps({"kind": "json", "text": text})
