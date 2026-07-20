"""Abstract base for cross-package subclass discovery without explicit registration."""

from abc import ABCMeta, abstractmethod
from collections.abc import Iterable, Iterator
from types import ModuleType
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison

from pyrig_runtime import rig
from pyrig_runtime.core.dependencies.discovery import (
    discover_subclasses_across_dependencies,
)
from pyrig_runtime.core.introspection.classes import (
    discard_abstract_classes,
    discard_parent_classes,
)
from pyrig_runtime.core.strings import fully_qualified_name


class DependencySubclassMeta(ABCMeta):
    """Metaclass backing `DependencySubclass` with the cached `I`/`L` properties."""

    @property
    def I[C: DependencySubclass](cls: type[C]) -> C:  # noqa: E743, N802
        """Return a cached instance of the leaf subclass.

        The instance is created once per class and reused on every subsequent
        access.

        Returns:
            An instance of the leaf subclass, or of the class itself if no
            subclasses exist.

        Raises:
            RuntimeError: If more than one leaf subclass is found.
        """
        if "_instance" not in cls.__dict__:
            cls._instance = cls.L()
        return cls._instance

    @property
    def L[C: DependencySubclass](cls: type[C]) -> type[C]:  # noqa: N802
        """Return the cached leaf subclass type.

        The result is cached per class and reused on every subsequent access.

        Returns:
            The single leaf subclass type, or the class itself if no
            subclasses exist. May be abstract.

        Raises:
            RuntimeError: If more than one leaf subclass is found.
        """
        if "_leaf" not in cls.__dict__:
            cls._leaf = cls.leaf()
        return cls._leaf

    def __str__(cls) -> str:
        """Return the fully qualified name of this class."""
        return fully_qualified_name(cls)


class DependencySubclass(metaclass=DependencySubclassMeta):
    """Abstract base enabling plugin-style subclass discovery across installed packages.

    Subclasses declare a discovery scope by overriding the discovery hook,
    and the base class automatically finds all subclass implementations defined
    in that scope across every installed package that depends on the root
    package. The scope may be a single module, to keep discovery narrow, or a
    whole sub-package, to widen it to a full hierarchy. No explicit
    registration is required.
    """

    @classmethod
    @abstractmethod
    def discovery_module(cls) -> ModuleType:
        """Return the module or package that scopes discovery of this class.

        Every concrete subclass must override this to declare where its
        implementation classes live. Returning a package widens discovery to
        that package's whole module hierarchy; returning a plain module keeps
        discovery narrow to that single module.

        The base implementation returns `pyrig_runtime.rig`.

        Returns:
            The module or package that scopes the search for concrete
            implementations of this class.
        """
        return rig

    @classmethod
    def concrete_subclasses(cls) -> Iterator[type[Self]]:
        """Yield all concrete leaf subclasses discovered across dependent packages.

        Yields:
            Non-abstract leaf subclass types.
        """
        return discard_abstract_classes(cls.subclasses())

    @classmethod
    def leaf(cls) -> type[Self]:
        """Return the single leaf subclass found across dependent packages.

        If no subclasses are found, the class itself is returned.

        Returns:
            The single leaf subclass type, or the class itself if no
            subclasses are found. May be abstract.

        Raises:
            RuntimeError: If more than one leaf subclass is discovered across
                the dependent packages because defining multiple leaf subclasses
                is ambiguous.
        """
        subclasses = cls.subclasses()
        leaf = next(subclasses, cls)
        second = next(subclasses, None)
        if second is None:
            return leaf

        subclasses_formatted = "\n".join(
            fully_qualified_name(subcls) for subcls in (leaf, second, *subclasses)
        )
        msg = f"multiple leaf subclasses found:\n{subclasses_formatted}"
        raise RuntimeError(msg)

    @classmethod
    def subclasses(cls) -> Iterator[type[Self]]:
        """Yield all subclasses discovered across installed dependent packages.

        Only leaf-level subclasses are yielded; any intermediate parent classes
        that also appear in the result set are omitted.

        Yields:
            Leaf subclass types.
        """
        return discard_parent_classes(
            discover_subclasses_across_dependencies(
                cls,
                module=cls.discovery_module(),
            ),
        )

    @classmethod
    def sort_key(cls) -> "SupportsRichComparison":
        """Return the sort key used to order this class relative to peer subclasses.

        Override to sort by priority, numeric position, or any other criterion.
        The default returns the class name, giving alphabetical ordering.

        Returns:
            A value comparable with `<` against the sort keys of other
            subclasses.
        """
        return cls.__name__

    @classmethod
    def sorted_subclasses(
        cls,
        subclasses: Iterable[type[Self]],
    ) -> list[type[Self]]:
        """Sort the given subclasses using each subclass's `sort_key()`.

        Does not perform any discovery.

        Args:
            subclasses: Subclass types to sort.

        Returns:
            The same subclass types sorted by their `sort_key()`.
        """
        return sorted(
            subclasses,
            key=lambda subclass: subclass.sort_key(),
        )

    def __str__(self) -> str:
        """Return the fully qualified class name of this instance."""
        return str(self.__class__)
