"""Utilities for introspecting and filtering Python classes."""

import inspect
from collections.abc import Iterable, Iterator


def discard_abstract_classes[T](classes: Iterable[type[T]]) -> Iterator[type[T]]:
    """Filter out abstract classes from a collection.

    A class is considered abstract when it has one or more unimplemented
    abstract methods and therefore cannot be instantiated directly.

    Args:
        classes: Iterable of class types to filter.

    Yields:
        Concrete (non-abstract) classes from the input.
    """
    return (cls for cls in classes if not inspect.isabstract(cls))


def discard_parent_classes[T](
    classes: Iterable[type[T]],
) -> Iterator[type[T]]:
    """Yield only leaf classes, removing any ancestors present in the collection.

    A class is kept only when no other class in the collection is a strict
    subclass of it. The original iterable is not modified.

    Args:
        classes: Iterable of class types to filter.

    Yields:
        Classes that have no subclasses present in the same collection.
    """
    classes = set(classes)
    parents = {parent for cls in classes for parent in cls.__mro__[1:]}
    return (cls for cls in classes if cls not in parents)


def discover_subclasses[T](cls: type[T]) -> set[type[T]]:
    """Discover all transitive subclasses of `cls` currently loaded in memory.

    Does not trigger any imports, so only subclasses from already-imported
    modules are included in the result.

    Args:
        cls: Base class to find subclasses of.

    Returns:
        Set of all transitive subclass types, excluding `cls` itself.
    """
    visited: set[type[T]] = set()
    stack = cls.__subclasses__()
    while stack:
        subclass = stack.pop()
        if subclass in visited:
            continue
        visited.add(subclass)
        stack.extend(subclass.__subclasses__())
    return visited
