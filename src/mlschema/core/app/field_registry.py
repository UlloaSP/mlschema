"""mlschema.core.app.field_registry
===================================
Corporate registry of *FieldStrategy*.

This unit orchestrates strategy resolution both by logical identifier
(``type_name``) and by NumPy/pandas ``dtype``, allowing the application
layer to ask:

* "Give me the *strategy* for the logical type ``"number"``"; or
* "Give me the *strategy* capable of handling a ``dtype('float64')``".

Example usage
```python
 from numpy import dtype
 from mlschema.core.app.field_strategy import FieldStrategy
 class DummyStrategy(FieldStrategy):
     def __init__(self):
         super().__init__(
             type_name="dummy",
             schema_cls=BaseField,  # fictitious type
             dtypes=("int64",),
         )
 registry = FieldRegistry()
 registry.register(DummyStrategy())
 assert registry.strategy_for_name("dummy").type_name == "dummy"
 assert registry.strategy_for_dtype(dtype("int64")).type_name == "dummy"
```
"""

from __future__ import annotations

from numpy import dtype as np_dtype

from mlschema.core.app.field_strategy import FieldStrategy


class FieldRegistry:
    """Manages the lifecycle of registered *FieldStrategy* instances.

    Internally maintains two parallel indices:

    * ``_by_name``   - Mapping "type_name" → strategy.
    * ``_by_dtype``  - Mapping "dtype.name" → strategy.

    Both structures are kept coherent in each registration, update, or
    removal operation. The registry is not thread-safe by design (the
    expected usage is write-once, read-many in inference processes).
    """

    def __init__(self) -> None:
        """Initialize empty internal containers."""
        self._by_name: dict[str, FieldStrategy] = {}
        self._by_dtype: dict[str, FieldStrategy] = {}

    # ------------------------------------------------------------------ #
    # CRUD                                                               #
    # ------------------------------------------------------------------ #
    def register(self, strategy: FieldStrategy, *, overwrite: bool = False) -> None:
        """Register a new strategy.

        Parameters
        ----------
        strategy:
            Instance of :class:`FieldStrategy` to register.
        overwrite:
            If *True*, an existing registration with the same ``type_name`` or
            ``dtype`` will be replaced instead of raising an exception.

        Raises
        ------
        ValueError
            If a strategy already exists for that ``type_name`` or any of
            its ``dtype`` and ``overwrite`` is *False*.
        """
        name = strategy.type_name
        if not overwrite and name in self._by_name:
            raise ValueError(f"Strategy '{name}' already exists.")

        # Register by logical name
        self._by_name[name] = strategy

        # Register for each supported dtype
        for dt in strategy.dtypes:
            key = self._normalize_dtype(dt)
            if key in self._by_dtype and not overwrite:
                raise ValueError(f"dtype '{key}' already linked to another strategy.")
            self._by_dtype[key] = strategy

    def update(self, strategy: FieldStrategy) -> None:
        """Replace the existing strategy with the same ``type_name``.

        Equivalent to calling :meth:`register` with ``overwrite=True``.
        """
        self.register(strategy, overwrite=True)

    def unregister(self, type_name: str) -> None:
        """Remove a strategy from the registry.

        Parameters
        ----------
        type_name:
            Logical identifier of the field type to purge.
        """
        strat = self._by_name.pop(type_name, None)
        if strat:
            # Purge associated dtypes
            for dt in strat.dtypes:
                self._by_dtype.pop(self._normalize_dtype(dt), None)

    def strategy_for_name(self, type_name: str) -> FieldStrategy | None:
        """Return the strategy associated with ``type_name`` or ``None``."""
        return self._by_name.get(type_name)

    def strategy_for_dtype(self, dtype: str | np_dtype) -> FieldStrategy | None:
        """Return the strategy capable of handling ``dtype`` or ``None``."""
        return self._by_dtype.get(self._normalize_dtype(dtype))

    @staticmethod
    def _normalize_dtype(dtype) -> str:
        """Normalize dtype to string representation."""
        if hasattr(dtype, "name"):
            # Handle structured dtypes specially to include field information
            if hasattr(dtype, "names") and dtype.names is not None:
                return str(dtype)
            return dtype.name
        return str(dtype)
