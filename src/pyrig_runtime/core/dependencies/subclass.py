"""Abstract base for cross-package subclass discovery without explicit registration."""

import json
from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator
from functools import cache
from types import ModuleType
from typing import Any, Self, TypeVar

from pyrig_runtime import rig
from pyrig_runtime.core.dependencies.discovery import (
    discover_subclasses_across_dependencies,
)
from pyrig_runtime.core.introspection.classes import (
    classproperty,
    discard_abstract_classes,
    discard_parent_classes,
)

T = TypeVar("T", bound="DependencySubclass")


class DependencySubclass(ABC):
    """Abstract base enabling plugin-style subclass discovery across installed packages.

    Subclasses declare a sub-package scope by overriding the discovery hook,
    and the base class automatically finds all subclass implementations defined
    in that sub-package across every installed package that depends on the root
    package. No explicit registration is required.
    """

    def __str__(self) -> str:
        """Return the fully qualified class name of this instance."""
        return f"{self.__module__}.{self.__class__.__name__}"

    @classmethod
    @abstractmethod
    def dependency_package(cls) -> ModuleType:
        """Return the sub-package that scopes subclass discovery for this hierarchy.

        Every concrete subclass must override this to return the sub-package
        where its own implementations are defined. The returned module's root
        package determines which installed packages are searched.

        The base implementation returns `pyrig_runtime.rig`, making it callable
        via `super()` as a fallback or when calling `subclasses()` directly on
        `DependencySubclass` itself.

        Returns:
            Package module whose path pattern is replicated across dependent
            packages to locate the modules to search.
        """
        return rig

    @classmethod
    def sort_key(cls) -> Any:
        """Return a stable sort key used by `subclasses_sorted()` to order subclasses.

        Override to sort by priority, numeric position, or any other criterion.
        The default returns the class name, giving alphabetical ordering.

        Returns:
            A value that can be compared with other sort keys using `<`.
        """
        return cls.__name__

    @classproperty
    @cache  # noqa: B019  # false warning bc of custom classproperty decorator
    def I(cls) -> Self:  # noqa: E743, N802, N805
        """Return a cached instance of the leaf subclass.

        The instance is created once per class and reused on every subsequent
        access. Equivalent to instantiating the result of `cls.L`.

        Returns:
            An instance of the leaf subclass.

        Raises:
            RuntimeError: If more than one leaf subclass is found.
        """
        return cls.L()

    @classproperty
    @cache  # noqa: B019  # false warning bc of custom classproperty decorator
    def L(cls) -> type[Self]:  # noqa: N802, N805
        """Return the cached leaf subclass type.

        Equivalent to `leaf()`, but the result is cached so repeated accesses
        do not re-run discovery.

        Returns:
            The single leaf subclass type. May be abstract.

        Raises:
            RuntimeError: If more than one leaf subclass is found.
        """
        return cls.leaf()

    @classmethod
    def leaf(cls) -> type[Self]:
        """Return the single leaf subclass found across dependent packages.

        Calls `subclasses()` and tolerates at most one result. If no subclasses
        are found, the class itself is returned. Defining more than one leaf
        subclass across dependent packages is ambiguous and raises `RuntimeError`.

        Returns:
            The sole leaf subclass type. May be abstract.

        Raises:
            RuntimeError: If more than one subclass is discovered across
                the dependent packages.
        """
        subclasses = cls.subclasses()
        leaf = next(subclasses, cls)
        second = next(subclasses, None)
        if second is None:
            return leaf

        msg = f"""Multiple leaf subclasses found for {cls}.
Defining multiple leaf subclasses is ambiguous.
This can happen if more than one leaf subclass is defined
across all the dependent packages.

Found subclasses:
{json.dumps([str(subcls) for subcls in (leaf, second, *subclasses)], indent=4)}"""
        raise RuntimeError(msg)

    @classmethod
    def concrete_subclasses(cls) -> Iterator[type[Self]]:
        """Yield all non-abstract subclasses discovered across dependent packages.

        Equivalent to `subclasses()` with abstract classes removed.

        Yields:
            Non-abstract subclass types.
        """
        return discard_abstract_classes(cls.subclasses())

    @classmethod
    def subclasses(cls) -> Iterator[type[Self]]:
        """Yield all subclasses discovered across the package ecosystem.

        Searches every installed package that depends on the root package of
        `dependency_package()`. Intermediate parent classes are discarded,
        leaving only the outermost leaf-level subclasses.

        Yields:
            Subclass types with intermediate parent classes removed.
        """
        return discard_parent_classes(
            discover_subclasses_across_dependencies(
                cls,
                package=cls.dependency_package(),
            )
        )

    @classmethod
    def subclasses_sorted(cls, subclasses: Iterable[type[Self]]) -> list[type[Self]]:
        """Sort the given subclasses using each subclass's `sort_key()`.

        Does not perform any discovery. Pass any iterable of subclass types
        to produce a deterministically ordered list.

        Args:
            subclasses: Subclass types to sort.

        Returns:
            The same subclass types sorted by their `sort_key()`.
        """
        return sorted(subclasses, key=lambda subclass: subclass.sort_key())
