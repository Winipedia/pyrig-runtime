"""Abstract base for cross-package subclass discovery without explicit registration."""

from abc import ABCMeta, abstractmethod
from collections.abc import Iterable, Iterator
from operator import methodcaller
from types import ModuleType
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison

from pyrig_runtime import rig
from pyrig_runtime.core.dependencies.discovery import (
    subclasses_across_dependencies,
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
            TypeError: If the leaf subclass is abstract and cannot be
                instantiated.
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

    Subclasses declare a discovery scope by overriding the discovery hook, and
    the base class automatically finds every subclass defined at that scope,
    both within its root package and across every installed package that
    depends on it. The scope may be a single module, to keep discovery
    narrow, or a whole sub-package, to widen it to a full module hierarchy.
    No explicit registration is required.
    """

    @classmethod
    @abstractmethod
    def discovery_module(cls) -> ModuleType:
        """Return the module or package that scopes discovery of this class.

        Used by `subclasses()` to scope cross-package discovery to the correct
        namespace. Every concrete subclass must override this to declare where its
        own implementation classes live: returning a package widens discovery to
        that package's whole module hierarchy, while returning a plain module
        keeps discovery narrow to that single module.

        The base implementation returns `pyrig_runtime.rig`.

        Returns:
            The module or package that scopes the search for this class's
            subclasses.

        Note:
            The returned module's root package must be `pyrig_runtime` itself
            or one of its installed dependents; otherwise discovery fails.
        """
        return rig

    @classmethod
    def concrete_subclasses(cls) -> Iterator[type[Self]]:
        """Yield all concrete leaf subclasses found within the declared discovery scope.

        Yields:
            Non-abstract leaf subclass types.
        """
        return discard_abstract_classes(cls.subclasses())

    @classmethod
    def leaf(cls) -> type[Self]:
        """Return the single leaf subclass found within the declared discovery scope.

        If no subclasses are found, the class itself is returned.

        Returns:
            The single leaf subclass type, or the class itself if no
            subclasses are found. May be abstract.

        Raises:
            RuntimeError: If more than one leaf subclass is discovered within
                the discovery scope because defining multiple leaf subclasses
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
        """Yield all subclasses discovered within the declared discovery scope.

        Only leaf-level subclasses are yielded; any intermediate parent classes
        that also appear in the result set are omitted.

        Yields:
            Leaf subclass types.
        """
        return discard_parent_classes(
            subclasses_across_dependencies(
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
            key=methodcaller(cls.sort_key.__name__),
        )

    def __str__(self) -> str:
        """Return the fully qualified name of this instance's class."""
        return str(self.__class__)
