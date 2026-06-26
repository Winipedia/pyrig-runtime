"""Subclass discovery and module-import utilities scoped to a package."""

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

    All modules within `package` are guaranteed to have been imported before
    the result is returned, ensuring subclasses from previously unimported
    modules are included. Only subclasses defined in a proper sub-module of
    `package` are returned; classes defined in the root package module itself
    are excluded.

    Args:
        cls: Base class whose subclasses should be discovered.
        package: Package to scope discovery to.

    Returns:
        Set of all transitive subclass types of `cls` defined within
        `package`, excluding `cls` itself.
    """
    register_package_modules(package)
    subclasses = discover_subclasses(cls)
    # remove all not in the package
    return {
        subclass
        for subclass in subclasses
        if subclass.__module__.startswith(package.__name__ + ".")
    }


@cache
def register_package_modules(package: ModuleType) -> None:
    """Import all modules in a package hierarchy to trigger their side effects.

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
