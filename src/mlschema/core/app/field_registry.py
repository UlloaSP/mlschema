"""mlschema.core.app.field_registry
===================================
Registro corporativo de *FieldStrategy*.

Esta unidad orquesta la resolución de estrategias tanto por identificador
lógico (``type_name``) como por ``dtype`` de NumPy/pandas, lo que permite
que la capa de aplicación pregunte:

* «Dame la *strategy* para el tipo lógico ``"number"``»; o
* «Dame la *strategy* capaz de manejar un ``dtype('float64')``».

Ejemplo de uso
>>> from numpy import dtype
>>> from mlschema.core.app.field_strategy import FieldStrategy
>>> class DummyStrategy(FieldStrategy):
...     def __init__(self):
...         super().__init__(
...             type_name="dummy",
...             schema_cls=BaseField,  # tipo ficticio
...             dtypes=("int64",),
...         )
>>> registry = FieldRegistry()
>>> registry.add_strategy(DummyStrategy())
>>> assert registry.strategy_for_name("dummy").type_name == "dummy"
>>> assert registry.strategy_for_dtype(dtype("int64")).type_name == "dummy"
"""

from __future__ import annotations

from numpy import dtype as np_dtype
from pandas import api

from mlschema.core.app.field_strategy import FieldStrategy


class FieldRegistry:
    """Maneja el *lifecycle* de las *FieldStrategy* registradas.

    Internamente mantiene dos índices paralelos:

    * ``_by_name``   – Mapeo «type_name» → estrategia.
    * ``_by_dtype``  – Mapeo «dtype.name» → estrategia.

    Ambas estructuras se mantienen coherentes en cada operación de alta,
    actualización o baja. El registro no es *thread‑safe* por diseño (el
    uso esperado es *write‑once, read‑many* en procesos de inferencia).
    """

    def __init__(self) -> None:
        """Inicializa los contenedores internos vacíos."""
        self._by_name: dict[str, FieldStrategy] = {}
        self._by_dtype: dict[str, FieldStrategy] = {}

    # ------------------------------------------------------------------ #
    # CRUD                                                               #
    # ------------------------------------------------------------------ #
    def register(self, strategy: FieldStrategy, *, overwrite: bool = False) -> None:
        """Registra una nueva estrategia.

        Parameters
        ----------
        strategy:
            Instancia de :class:`FieldStrategy` a registrar.
        overwrite:
            Si *True*, un registro existente con el mismo ``type_name`` o
            ``dtype`` será reemplazado en lugar de lanzar excepción.

        Raises
        ------
        ValueError
            Si ya existe una estrategia para ese ``type_name`` o alguno de
            sus ``dtype`` y ``overwrite`` es *False*.
        """
        name = strategy.type_name
        if not overwrite and name in self._by_name:
            raise ValueError(f"Strategy '{name}' already exists.")

        # Registrar por nombre lógico
        self._by_name[name] = strategy

        # Registrar por cada dtype soportado
        for dt in strategy.dtypes:
            key = self._normalize_dtype(dt)
            if key in self._by_dtype and not overwrite:
                raise ValueError(f"dtype '{key}' ya vinculado a otra strategy.")
            self._by_dtype[key] = strategy

    def update(self, strategy: FieldStrategy) -> None:
        """Reemplaza la estrategia existente con igual ``type_name``.

        Equivale a invocar :meth:`add_strategy` con ``overwrite=True``.
        """
        self.register(strategy, overwrite=True)

    def unregister(self, type_name: str) -> None:
        """Elimina una estrategia del registro.

        Parameters
        ----------
        type_name:
            Identificador lógico del tipo de campo a purgar.
        """
        strat = self._by_name.pop(type_name, None)
        if strat:
            # Purgar los dtype asociados
            for dt in strat.dtypes:
                self._by_dtype.pop(self._normalize_dtype(dt), None)

    # ------------------------------------------------------------------ #
    # Queries                                                            #
    # ------------------------------------------------------------------ #
    def strategy_for_name(self, type_name: str) -> FieldStrategy | None:
        """Retorna la estrategia asociada a ``type_name`` o ``None``."""
        return self._by_name.get(type_name)

    def strategy_for_dtype(self, dtype: str | np_dtype) -> FieldStrategy | None:
        """Retorna la estrategia capaz de manejar ``dtype`` o ``None``."""
        return self._by_dtype.get(self._normalize_dtype(dtype))

    # ------------------------------------------------------------------ #
    # Utils                                                              #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _normalize_dtype(dtype: str | np_dtype) -> str:
        """Devuelve el nombre estandarizado del ``dtype``.

        Parameters
        ----------
        dtype:
            Instancia o nombre del ``dtype``.

        Returns
        -------
        str
            Nombre canónico del ``dtype``.
        """
        return (
            dtype.name
            if isinstance(dtype, np_dtype | api.extensions.ExtensionDtype)
            else str(dtype)
        )
