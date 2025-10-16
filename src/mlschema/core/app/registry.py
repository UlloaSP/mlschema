from __future__ import annotations

from typing import Any

from mlschema.core.app.strategy import Strategy
from mlschema.core.exceptions import (
    StrategyDtypeAlreadyRegisteredError,
    StrategyNameAlreadyRegisteredError,
)
from mlschema.core.util import normalize_dtype


class Registry:
    """Manages the lifecycle of registered *Strategy* instances."""

    def __init__(self) -> None:
        """Initialize empty internal containers.

        The registry maintains two parallel indexes for efficient lookups:

        * ``_by_name`` - Maps logical type names (e.g., "number") to Strategy instances
        * ``_by_dtype`` - Maps normalized dtype names (e.g., "float64") to Strategy instances

        Both structures are kept coherent in each registration, update, or
        removal operation. The registry is not thread-safe by design (the
        expected usage is write-once, read-many in inference processes).
        """
        self._by_name: dict[str, Strategy] = {}
        self._by_dtype: dict[str, Strategy] = {}

    def register(self, strategy: Strategy, *, overwrite: bool = False) -> None:
        """Register a new strategy.

        Args:
            strategy: Instance of :class:`Strategy` to register.
            overwrite: If True, an existing registration with the same type_name or dtype will be replaced instead of raising an exception.

        Raises:
            StrategyNameAlreadyRegisteredError: If a strategy already exists for that type_name and overwrite is False.
            StrategyDtypeAlreadyRegisteredError: If a strategy already exists for any of its dtype and overwrite is False.
        """
        if not overwrite and strategy.type_name in self._by_name:
            raise StrategyNameAlreadyRegisteredError(strategy.type_name)

        normalized_keys = set(map(normalize_dtype, strategy.dtypes))

        for key in normalized_keys:
            if not overwrite and key in self._by_dtype:
                raise StrategyDtypeAlreadyRegisteredError(key)

        self._by_name[strategy.type_name] = strategy

        for key in normalized_keys:
            self._by_dtype[key] = strategy

    def update(self, strategy: Strategy) -> None:
        """Replace the existing strategy with the same ``type_name``.

        Equivalent to calling :meth:`register` with ``overwrite=True``.

        Args:
            strategy: Instance of :class:`Strategy` to update.
        """
        self.register(strategy, overwrite=True)

    def unregister(self, type_name: str) -> None:
        """Remove a strategy from the registry.

        Args:
            type_name: The logical identifier of the strategy to remove.
        """
        strat = self._by_name.pop(type_name, None)
        if strat is not None:
            self._by_dtype = {k: v for k, v in self._by_dtype.items() if v is not strat}

    def strategy_for_name(self, type_name: str) -> Strategy | None:
        """Return the strategy associated with ``type_name`` or ``None``.

        Args:
            type_name: Logical identifier of the field type to look up.

        Returns:
            Strategy instance for the given type name, or None if not found.
        """
        return self._by_name.get(type_name)

    def strategy_for_dtype(self, dtype: str | Any) -> Strategy | None:
        """Return the strategy capable of handling ``dtype`` or ``None``.

        Args:
            dtype: Pandas dtype string or dtype object to look up.

        Returns:
            Strategy instance that handles the given dtype, or None if not found.
        """
        return self._by_dtype.get(normalize_dtype(dtype))
