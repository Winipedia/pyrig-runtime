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
    generate_class,
)
from pyrig_runtime.core.strings import fully_qualified_name


class DependencySubclassMeta(ABCMeta):
    """Metaclass backing `DependencySubclass` with the cached `I`/`L` properties."""

    @property
    def I[C: DependencySubclass](cls: type[C]) -> C:  # noqa: E743, N802
        """Return a cached instance of `L`.

        The instance is created once per class and reused on every subsequent
        access.

        Returns:
            An instance of `L`.

        Raises:
            TypeError: If `L` is abstract and cannot be instantiated, or if
                resolving `L` itself raises.
        """
        if "_instance" not in cls.__dict__:
            cls._instance = cls.L()
        return cls._instance

    @property
    def L[C: DependencySubclass](cls: type[C]) -> type[C]:  # noqa: N802
        """Return the cached result of `leaf()`.

        Computed once per class on first access and reused on every
        subsequent access.

        Returns:
            The same value `leaf()` returns for this class.

        Raises:
            TypeError: If `leaf()` cannot resolve a single type for this
                class.
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
        """Return the single leaf subclass, or a merge of them if several are found.

        If no subclasses are found, the class itself is returned. If more
        than one leaf subclass is found, a new subclass inheriting from
        every one of them is generated and returned instead.

        Returns:
            The single leaf subclass type, the class itself if none are
            found, or a generated subclass combining every leaf if more
            than one is found. May be abstract.

        Raises:
            TypeError: If the discovered leaf subclasses cannot be
                combined into a single class.

        Note:
            Discovery runs fresh on every call, and merging generates a
            new type each time, so two calls do not return the identical
            object when leaves are merged — only `L` caches a stable
            result. The generated subclass's bases follow the order of
            `subclasses()`, which is stable across calls but reflects
            discovery order rather than any deliberate priority — so
            which leaf's behavior wins for any method they both define
            should not be relied upon.
        """
        subclasses = cls.subclasses()
        leaf = next(subclasses, cls)
        if (second := next(subclasses, None)) is None:
            return leaf

        return generate_class(
            name=cls.__name__,
            bases=(leaf, second, *subclasses),
        )

    @classmethod
    def subclasses(cls) -> Iterator[type[Self]]:
        """Yield all subclasses discovered within the declared discovery scope.

        Only leaf-level subclasses are yielded; any intermediate parent classes
        that also appear in the result set are omitted.

        Yields:
            Leaf subclass types.
        """
        return discard_parent_classes(
            cls.discovered_subclasses(),
        )

    @classmethod
    def discovered_subclasses(cls) -> Iterator[type[Self]]:
        """Yield every subclass discovered within the declared discovery scope.

        Includes intermediate parent classes; unlike `subclasses()`, the
        result is not filtered down to leaves.

        Yields:
            Subclass types found anywhere in the discovery scope. The
            order is stable across calls but reflects discovery order,
            not any deliberate priority.
        """
        return subclasses_across_dependencies(
            cls,
            module=cls.discovery_module(),
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
