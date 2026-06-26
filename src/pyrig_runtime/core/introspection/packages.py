"""Python package utilities."""

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

    All modules in `package` are imported before subclass collection so that
    classes in unimported modules are included. Only subclasses that are
    defined in a proper sub-module of `package` are returned; classes defined
    in the root package module itself are excluded.

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
    """Import all modules in a package to trigger their side effects.

    Ensures every module in the package is present in `sys.modules` and has
    executed, so that classes and functions defined in them are registered.

    Args:
        package: Package to import all modules from.

    Note:
        Cached so that repeated calls with the same package skip redundant
        imports — a module only needs to be registered once.
    """
    # exhaust the generator to trigger imports, but ignore the output
    _ = tuple(walk_package(package))


def walk_package(package: ModuleType) -> Iterator[tuple[ModuleType, bool]]:
    """Recursively walk and import all modules in a package hierarchy.

    Performs a depth-first traversal of `package` and its sub-packages,
    importing each visited module as a side effect. The root `package`
    itself is not yielded.

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
