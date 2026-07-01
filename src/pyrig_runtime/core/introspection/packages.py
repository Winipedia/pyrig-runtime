"""Subclass discovery scoped to a package's full module hierarchy."""

from collections.abc import Iterator
from functools import cache
from types import ModuleType

from pyrig_runtime.core.introspection.classes import discover_subclasses
from pyrig_runtime.core.introspection.modules import iter_modules


def discover_subclasses_across_package[T](
    cls: type[T],
    package: ModuleType,
) -> set[type[T]]:
    """Discover all subclasses of `cls` defined within a package.

    The package is scanned recursively, so subclasses are found in its
    sub-modules at any nesting depth, including ones not yet imported when this
    is called. Only subclasses whose defining module is a proper sub-module of
    `package` are returned; a class defined directly in the package's own
    `__init__` module is not discovered, so implementations belong in
    sub-modules rather than the package `__init__`.

    Args:
        cls: Base class whose subclasses should be discovered.
        package: Package to scope discovery to.

    Returns:
        Set of all transitive subclass types of `cls` defined within
        `package`, excluding `cls` itself.
    """
    register_package_modules(package)
    subclasses = discover_subclasses(cls)
    return {
        subclass
        for subclass in subclasses
        if subclass.__module__.startswith(f"{package.__name__}.")
    }


@cache
def register_package_modules(package: ModuleType) -> None:
    """Ensure all modules in a package hierarchy are imported.

    Args:
        package: Root package whose entire module hierarchy will be imported.

    Note:
        Cached per package — subsequent calls with the same package do
        nothing.
    """
    # exhaust the generator to trigger imports, but ignore the output
    _ = tuple(walk_package(package))


def walk_package(package: ModuleType) -> Iterator[tuple[ModuleType, bool]]:
    """Walk all modules in a package hierarchy, recursing into sub-packages.

    Importing each visited module is a side effect of iteration. The root
    `package` itself is not yielded.

    Args:
        package: Root package to start traversal from.

    Yields:
        `(module, is_package)` pairs for each visited module, where
        `is_package` is `True` when the module is itself a sub-package.
    """
    for module, is_package in iter_modules(package):
        if is_package:
            yield module, True
            yield from walk_package(module)
        else:
            yield module, False
