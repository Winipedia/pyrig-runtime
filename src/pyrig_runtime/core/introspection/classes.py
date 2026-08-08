"""Utilities for introspecting and filtering Python classes."""

import inspect
from collections.abc import Iterable, Iterator
from itertools import filterfalse
from types import FunctionType
from typing import Any, cast


def discard_abstract_classes[T](classes: Iterable[type[T]]) -> Iterator[type[T]]:
    """Filter out abstract classes from a collection.

    A class is considered abstract when it has one or more unimplemented
    abstract methods and therefore cannot be instantiated directly.

    Args:
        classes: Iterable of class types to filter.

    Yields:
        Concrete (non-abstract) classes from the input.
    """
    return filterfalse(inspect.isabstract, classes)


def discard_parent_classes[T](
    classes: Iterable[type[T]],
) -> Iterator[type[T]]:
    """Yield only leaf classes, removing any ancestors present in the collection.

    A class is kept only when no other class in the collection is a strict
    subclass of it. The original iterable is not modified.

    Args:
        classes: Iterable of class types to filter.

    Yields:
        Classes that have no subclasses present in the same collection, in
        the same order as `classes`.
    """
    classes = tuple(classes)
    parents = {parent for cls in classes for parent in cls.__mro__[1:]}
    return filterfalse(parents.__contains__, classes)


def discover_subclasses[T](cls: type[T]) -> tuple[type[T], ...]:
    """Discover all transitive subclasses of `cls` currently loaded in memory.

    Does not trigger any imports, so only subclasses from already-imported
    modules are included in the result.

    Args:
        cls: Base class to find subclasses of.

    Returns:
        Tuple of all transitive subclass types, excluding `cls` itself.
    """
    visited: dict[type[T], None] = {}
    stack = cls.__subclasses__()
    while stack:
        subclass = stack.pop()
        if subclass in visited:
            continue
        visited[subclass] = None
        stack.extend(subclass.__subclasses__())
    return tuple(visited)


def generate_class[T](
    name: str,
    bases: tuple[type[T], ...],
    methods: Iterable[FunctionType] = (),
    namespace: dict[str, Any] | None = None,
) -> type[T]:
    """Dynamically create a class from base classes, methods, and attributes.

    Args:
        name: Name of the new class, used as its `__name__`.
        bases: Base classes the new class inherits from.
        methods: Functions to add to the class, each under its own `__name__`.
        namespace: Extra attributes for the class body, keyed by name. Mutated
            in place with the `methods` entries added on top, so a method
            whose name matches a key here overrides it. Defaults to a new,
            empty dict when omitted.

    Returns:
        The newly created class.

    Raises:
        TypeError: If `bases` cannot be combined into a class with a
            consistent method resolution order.

    Note:
        The generated class's `__module__` is whatever the underlying
        `type()` call infers from the calling context, which is not
        necessarily the caller's own module. Pass `"__module__"` in
        `namespace` to set it explicitly.
    """
    if namespace is None:
        namespace = {}
    for method in methods:
        namespace[method.__name__] = method
    return cast(
        "type[T]",
        type(
            name,
            bases,
            namespace,
        ),
    )
