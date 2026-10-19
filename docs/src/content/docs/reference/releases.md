---
title: Releases
description: How MLschema versions are published, how the documentation tracks them, and how to upgrade.
---

MLschema is pre-1.0. A minor release may change the field contract, and the
[changelog](/changelog/) marks every breaking change with migration notes. Pin the version you
tested and read the changelog before upgrading.

## How a version is published

The package version lives only in `pyproject.toml`. The **CI & Publish** workflow runs on every push
to `main`:

1. Lint, format check, type check, and tests run on Linux and Windows. The wheel and sdist
   are built and their PyPI description is checked.
2. The landing, documentation, and playground sites are built.
3. When both succeed and the version in `pyproject.toml` is not on PyPI yet, the distributions are
   published to [PyPI](https://pypi.org/project/mlschema/) and a GitHub release tagged
   `v<version>` is created. The release notes link to this changelog.
4. The three sites deploy from the files built in step 2.

Sites deploy on every successful push to `main`, whether or not a new package version was
published. A version already on PyPI is never published again, so documentation-only changes
reach the site without a release.

## Which version these pages describe

The published documentation follows `main`. Between releases it can describe changes that are
prepared but not yet on PyPI; the changelog lists them under **Unreleased**. Compare with the version
you have installed:

```python
from importlib.metadata import version

print(version("mlschema"))
```

Pages are written by hand, and their examples are checked against the library when the contract
changes. The outputs shown are what `infer_schema()` returns, including key order and float
formatting.

## Links

- [PyPI package and release history](https://pypi.org/project/mlschema/#history)
- [GitHub releases](https://github.com/UlloaSP/mlschema/releases)
- [Changelog](/changelog/)
