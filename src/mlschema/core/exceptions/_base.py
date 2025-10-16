from __future__ import annotations

from typing import Any


class MLSchemaError(Exception):
    """Project-root for every **mlschema** runtime failure.

    All domain-specific exceptions ultimately derive from this class,
    enabling both narrow and broad interception patterns:

    ```python
    try:
        schema = ms.build(df)
    except MLSchemaError as exc:  # catch-all
        logger.error("Schema failure: %s", exc, exc_info=True)
        raise HTTPException(422, detail=str(exc)) from exc
    ```

    Attributes:
        context: Optional, machine-friendly diagnostics (e.g., offending
            `dtype`, column name, strategy ID).  Contents are *stable* only
            for the public leaf exceptions; treat additional keys as
            informational.
    """

    def __init__(
        self, message: str | None = None, *, context: dict[str, Any] | None = None
    ) -> None:
        super().__init__(message or self.__class__.__name__)
        self.context: dict[str, Any] | None = context


class InvalidValueError(MLSchemaError, ValueError):
    """Standard signal for configuration or user-input violations.

    Raised when a supplied argument, configuration value, or runtime
    artefact fails validation.  Subclasses narrow the scope to
    specific domains (e.g., *registry* vs. *service* faults).

    Args
    ----
    param: Logical argument name that triggered the failure
        (``"dtype"``, ``"type_name"``, …).
    value: Offending value already *normalised* by the caller.
    message: Human-readable description.  If *None*, a neutral default is
        auto-generated.
    context: Arbitrary diagnostics for observability pipelines
        (e.g., ``{"strategy": "NumberStrategy"}``).

    Attributes:
    param: Same as the *param* constructor argument.
    value: Same as the *value* constructor argument.
    context: Same as the *context* constructor argument.
        Same as the *context* constructor argument.

    Examples
    --------
    ```python
    if dtype_key in registry:
        raise InvalidValueError(
            param="dtype",
            value=dtype_key,
            message=f"dtype {dtype_key!r} already mapped",
            context={"registered_strategy": registry[dtype_key]},
        )
    ```
    """

    def __init__(
        self,
        param: str,
        value: Any,
        message: str | None = None,
        *,
        context: dict[str, Any] | None = None,
    ) -> None:
        self.param: str = param
        self.value: Any = value
        default = f'Invalid value for "{param}": {value!r}.'
        super().__init__(message or default, context=context)
