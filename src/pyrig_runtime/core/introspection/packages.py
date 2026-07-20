"""Subclass discovery scoped by a module name prefix."""

from collections.abc import Iterator
from functools import cache
from types import ModuleType

from pyrig_runtime.core.introspection.modules import iter_modules


def is_package(module: ModuleType) -> bool:
    """Return `True` if `module` is a package rather than a plain module."""
    return hasattr(module, "__path__")


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
    for module, is_pkg in iter_modules(package):
        if is_pkg:
            yield module, True
            yield from walk_package(module)
        else:
            yield module, False
