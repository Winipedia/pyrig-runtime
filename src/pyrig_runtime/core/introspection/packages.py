"""Subclass discovery scoped by a module name prefix."""

from collections.abc import Iterator
from functools import cache
from types import ModuleType

from pyrig_runtime.core.introspection.classes import discover_subclasses
from pyrig_runtime.core.introspection.modules import iter_modules


def discover_subclasses_across_module[T](
    cls: type[T],
    module: ModuleType,
) -> set[type[T]]:
    """Discover all subclasses of `cls` whose module name starts with `module`.

    When `module` is a package, its full module hierarchy is imported first, so
    subclasses are found in its sub-modules at any nesting depth, including ones
    not yet imported when this is called. When `module` is a plain module, no
    import walking happens and only subclasses already defined are considered.

    A subclass matches when the dotted name of its defining module starts with
    `module.__name__`. This includes `module` itself, every sub-module of it,
    and any sibling module whose name shares that prefix (for example, scope
    `pkg.foo` also matches `pkg.foobar`). Choosing a plain module as the scope
    therefore narrows discovery to that one file, while choosing a package
    widens it to the whole hierarchy.

    Args:
        cls: Base class whose subclasses should be discovered.
        module: Module or package whose dotted name prefixes the discovery
            scope.

    Returns:
        Set of all subclass types of `cls` whose defining module name starts
        with `module.__name__`, excluding `cls` itself.
    """
    if is_package(module):
        register_package_modules(module)
    subclasses = discover_subclasses(cls)
    return {
        subclass
        for subclass in subclasses
        if subclass.__module__.startswith(module.__name__)
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


def is_package(module: ModuleType) -> bool:
    """Return `True` if `module` is a package rather than a plain module."""
    return hasattr(module, "__path__")
