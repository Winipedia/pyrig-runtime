"""Abstract base for cross-package subclass discovery without explicit registration."""

from abc import ABCMeta, abstractmethod
from collections import defaultdict
from collections.abc import Hashable, Iterable, Iterator
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
    filter_concrete_classes,
    filter_leaf_classes,
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
            TypeError: If `leaf()` raises.
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
    def concrete_leaves(cls) -> Iterator[type[Self]]:
        """Yield all concrete leaf subclasses found within the declared discovery scope.

        Yields:
            Non-abstract leaf subclass types.
        """
        return filter_concrete_classes(cls.leaves())

    @classmethod
    def leaf(cls) -> type[Self]:
        """Return the leaf subclass for this class's discovery scope.

        Returns the class itself if no subclasses are discovered. Otherwise
        returns the first value `leaves()` yields for this class: if every
        discovered leaf shares one merge key, that is this class's one
        true leaf; if leaves span more than one merge key, every group but
        the first encountered is silently discarded, so `leaf()` is only
        meaningful for hierarchies that resolve to a single merge key.

        Returns:
            The first leaf subclass type `leaves()` yields, or the class
            itself if none are found.

        Raises:
            TypeError: If the leaves in the first merge-key group cannot
                be combined into a single class.

        Note:
            Discovery runs fresh on every call, and merging generates a
            new type each time, so two calls do not return the identical
            object when leaves are merged — only `L` caches a stable
            result. Which merged leaf's behavior wins for any method
            they both define should not be relied upon.
        """
        return next(cls.leaves(), cls)

    @classmethod
    def leaves(cls) -> Iterator[type[Self]]:
        """Yield leaf subclasses discovered within the declared discovery scope.

        Only leaf-level subclasses are considered; any intermediate parent
        classes that also appear in the result are omitted. The remaining leaves
        are grouped by `merge_key()`: a group with a single leaf is yielded as-is,
        while a group with several leaves is combined into one newly generated subclass
        inheriting from every leaf in that group, letting independently-installed
        packages cooperatively extend the same class by sharing a merge key.

        Yields:
            Leaf subclass types, one per distinct `merge_key()` value.

        Raises:
            TypeError: If the leaves within a merge key group cannot be
                combined into a single class.
        """
        by_merge_key: dict[Hashable, list[type[Self]]] = defaultdict(list)
        for subclass in filter_leaf_classes(cls.subclasses()):
            by_merge_key[subclass.merge_key()].append(subclass)
        for subclasses in by_merge_key.values():
            subcls = subclasses[0]
            if len(subclasses) == 1:
                yield subcls
            else:
                yield generate_class(
                    name=subcls.__name__,
                    bases=tuple(subclasses),
                )

    @classmethod
    def subclasses(cls) -> Iterator[type[Self]]:
        """Yield every subclass discovered within the declared discovery scope.

        Includes intermediate parent classes; unlike `leaves()`, the
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

        Used by `sorted_subclasses()` to order a collection of subclasses.
        Override to sort by priority, numeric position, or any other criterion.
        The default returns the class name, giving alphabetical ordering.

        Returns:
            A value comparable with `<` against the sort keys of other
            subclasses.
        """
        return cls.__name__

    @classmethod
    def merge_key(cls) -> Hashable:
        """Return the key that decides which leaf subclasses get merged together.

        Leaf subclasses that return an equal merge key are combined into
        one generated subclass by `leaves()`; those with different keys
        stay apart. Override to group cooperating implementations under a
        shared key. The default returns the class name, so same-named
        leaf overrides across dependent packages merge automatically.

        Returns:
            A value comparable with `==` against the merge keys of other
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
