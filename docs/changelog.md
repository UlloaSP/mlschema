# Changelog

> This project adheres to [Semantic Versioning](https://semver.org/) and the principles defined in [Keep a Changelog](https://keepachangelog.com/).

---

## \[0.1.1] – *Upcoming*

### Added

* **Schema orchestration** via `mlschema.core.MLSchema`, enabling registration, hot‑swap, and removal of field strategies.
* **Built‑in strategies**: `TextStrategy`, `NumberStrategy`, `CategoryStrategy`, `BooleanStrategy`, and `DateStrategy`—covering 90 % of common DataFrame dtypes.
* **JSON schema generation** through `MLSchema.build(df)`, producing front‑end‑ready dictionaries.
* **Fallback mechanism**: unmapped dtypes default to `TextStrategy` when registered.
* **Custom extension API** based on `BaseField` (Pydantic) and `Strategy`, allowing domain‑specific controls.
* **Pydantic v2 validation hooks** for runtime integrity checks.
* **Documentation**: comprehensive *Home*, *Installation*, *Usage*, and *API Reference* sections.

### Changed

* N/A

### Deprecated

* N/A

### Removed

* N/A

### Fixed

* N/A

---

## Legend

* **Added** for new features.
* **Changed** for backward‑compatible enhancements.
* **Deprecated** for soon‑to‑be removed features.
* **Removed** for breaking changes that eliminate functionality.
* **Fixed** for any bug fixes.

> *All dates will be added upon tagged releases.*
