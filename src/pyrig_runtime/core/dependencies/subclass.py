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
from pyrig_runtime.core.strings import fully_qualified_name

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
        return fully_qualified_name(self.__class__)

    @classmethod
    @abstractmethod
    def dependency_package(cls) -> ModuleType:
        """Return the sub-package where this class's implementations are defined.

        Every concrete subclass must override this to return the sub-package
        module that contains its own implementation classes. The base class uses
        the returned module to scope cross-package subclass discovery.

        The base implementation returns `pyrig_runtime.rig`.

        Returns:
            The sub-package module to search for concrete implementations of
            this class.
        """
        return rig

    @classmethod
    def sort_key(cls) -> Any:
        """Return the sort key used to order this class relative to peer subclasses.

        Override to sort by priority, numeric position, or any other criterion.
        The default returns the class name, giving alphabetical ordering.

        Returns:
            A value comparable with `<` against the sort keys of other
            subclasses.
        """
        return cls.__name__

    @classproperty
    @cache  # noqa: B019
    def I(cls) -> Self:  # noqa: E743, N802, N805
        """Return a cached instance of the leaf subclass.

        The instance is created once per class and reused on every subsequent
        access.

        Returns:
            An instance of the leaf subclass, or of the class itself if no
            subclasses exist.

        Raises:
            RuntimeError: If more than one leaf subclass is found.
        """
        return cls.L()

    @classproperty
    @cache  # noqa: B019
    def L(cls) -> type[Self]:  # noqa: N802, N805
        """Return the cached leaf subclass type.

        The result is cached per class and reused on every subsequent access.

        Returns:
            The single leaf subclass type, or the class itself if no
            subclasses exist. May be abstract.

        Raises:
            RuntimeError: If more than one leaf subclass is found.
        """
        return cls.leaf()

    @classmethod
    def leaf(cls) -> type[Self]:
        """Return the single leaf subclass found across dependent packages.

        If no subclasses are found, the class itself is returned.

        Returns:
            The single leaf subclass type, or the class itself if no
            subclasses are found. May be abstract.

        Raises:
            RuntimeError: If more than one subclass is discovered across
                the dependent packages.
        """
        subclasses = cls.subclasses()
        leaf = next(subclasses, cls)
        second = next(subclasses, None)
        if second is None:
            return leaf

        subclasses_dump = json.dumps(
            [fully_qualified_name(subcls) for subcls in (leaf, second, *subclasses)],
            indent=4,
        )
        msg = f"""Multiple leaf subclasses found for {cls}.
Defining multiple leaf subclasses is ambiguous.
This can happen if more than one leaf subclass is defined
across all the dependent packages.

Found subclasses:
{subclasses_dump}"""
        raise RuntimeError(msg)

    @classmethod
    def concrete_subclasses(cls) -> Iterator[type[Self]]:
        """Yield all concrete leaf subclasses discovered across dependent packages.

        Yields:
            Non-abstract leaf subclass types.
        """
        return discard_abstract_classes(cls.subclasses())

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
                package=cls.dependency_package(),
            )
        )

    @classmethod
    def subclasses_sorted(cls, subclasses: Iterable[type[Self]]) -> list[type[Self]]:
        """Sort the given subclasses using each subclass's `sort_key()`.

        Does not perform any discovery.

        Args:
            subclasses: Subclass types to sort.

        Returns:
            The same subclass types sorted by their `sort_key()`.
        """
        return sorted(subclasses, key=lambda subclass: subclass.sort_key())
