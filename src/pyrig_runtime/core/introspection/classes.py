"""Utilities for introspecting and filtering Python classes."""

import inspect
from collections.abc import Callable, Iterable, Iterator


def discover_subclasses[T](cls: type[T]) -> set[type[T]]:
    """Discover all transitive subclasses of `cls` currently loaded in memory.

    Does not trigger any imports, so only subclasses from already-imported
    modules are included in the result.

    Args:
        cls: Base class to find subclasses of.

    Returns:
        Set of all transitive subclass types, excluding `cls` itself.
    """
    subclasses = set(cls.__subclasses__())
    for subclass in cls.__subclasses__():
        subclasses.update(discover_subclasses(subclass))
    return subclasses


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
    classes = set(classes)  # ensure we have a set for O(1) lookups
    return (
        cls
        for cls in classes
        if not any(
            candidate is not cls and issubclass(candidate, cls) for candidate in classes
        )
    )


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


class classproperty[T]:  # noqa: N801
    """Descriptor that exposes a property computed from the class, not an instance.

    Unlike `@property`, which requires an instance, `@classproperty` can be
    accessed directly on the class and also works correctly when accessed from
    an instance.

    Combine with `@functools.cache` on the underlying method to cache the
    computed value per class.

    Example:
        >>> class MyClass:
        ...     @classproperty
        ...     def cls_name(cls) -> str:
        ...         return cls.__name__.lower()
        ...
        >>> MyClass.cls_name
        'myclass'
    """

    __slots__ = ("fget",)

    def __init__(self, fget: Callable[..., T]) -> None:
        """Wrap `fget` as a class-level property descriptor."""
        self.fget = fget

    def __get__(self, obj: object, owner: type) -> T:
        """Invoke the getter with the owner class and return the result.

        Args:
            obj: The instance the attribute was accessed from, or `None`
                when accessed directly on the class. Not used.
            owner: The class through which the attribute is accessed.

        Returns:
            The value returned by `fget` when called with `owner`.
        """
        return self.fget(owner)
