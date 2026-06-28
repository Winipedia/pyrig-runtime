"""Utilities for Python modules."""

import logging
from collections.abc import Iterable, Iterator
from importlib import import_module
from pkgutil import iter_modules as pkgutil_iter_modules
from types import ModuleType
from typing import Any

from pyrig_runtime.core.constants import MISSING
from pyrig_runtime.core.wrappers import safe_call

logger = logging.getLogger(__name__)


def root_module(module: ModuleType) -> ModuleType:
    """Import and return the top-level package of the given module.

    For a module named `"package.subpackage.module"`, the module corresponding
    to `"package"` is returned. For a top-level module with no dots in its name,
    the module for that same name is returned.

    Args:
        module: Module to resolve the root package for.

    Returns:
        The module corresponding to the first segment of the dotted name.
    """
    return import_module(module.__name__.split(".")[0])


def safe_import_module(
    module_name: str, *args: Any, default: Any = MISSING, **kwargs: Any
) -> ModuleType | Any:
    """Import a module by name, with an optional fallback on failure.

    Any `Exception` raised during import — not just `ImportError` — is
    handled, so errors at module level (e.g., `ValueError` raised on
    import) are also covered.

    Args:
        module_name: Dotted module name (e.g., `"package.subpackage.module"`).
        *args: Positional arguments forwarded to `import_module`.
        default: Value to return if the import raises. If not provided,
            the exception propagates unchanged.
        **kwargs: Keyword arguments forwarded to `import_module`.

    Returns:
        The imported module, or `default` if an exception is raised and
        `default` was provided.
    """
    return safe_call(import_module, module_name, *args, **kwargs, default=default)


def replace_root_module_name(module: ModuleType, root_module_name: str) -> str:
    """Replace the root package segment in a module's fully qualified name.

    Only the first segment is replaced; later segments are left untouched even
    if they happen to share the old root's name.

    Args:
        module: Module whose name to transform.
        root_module_name: Root package name to substitute in.

    Returns:
        The module name with its first dotted segment replaced.

    Example:
        >>> from types import ModuleType
        >>> mod = ModuleType("some_package.sub.module")
        >>> replace_root_module_name(mod, "my_project")
        'my_project.sub.module'
    """
    module_current_start = module.__name__.split(".")[0]
    return module.__name__.replace(module_current_start, root_module_name, 1)


def import_modules(module_names: Iterable[str]) -> Iterator[ModuleType]:
    """Import multiple modules by name, lazily.

    Modules are imported on demand as the result is iterated, not eagerly.

    Args:
        module_names: Dotted module names to import.

    Yields:
        Each imported module, in the order the names are iterated.
    """
    return (import_module(name) for name in module_names)


def iter_modules(package: ModuleType) -> Iterator[tuple[ModuleType, bool]]:
    """Import and yield each direct child of a package, in discovery order.

    Only the immediate children are visited; nested sub-packages are not
    recursed into.

    Args:
        package: Package to iterate. Must have a `__path__` attribute
            (i.e., must be a package, not a plain module).

    Yields:
        `(module, is_package)` pairs where `module` is the imported child and
        `is_package` is `True` when the child is itself a sub-package.

    Note:
        Importing each child is a deliberate side effect — any module-level
        code in those children executes on demand as the iterator is consumed.
    """
    for _finder, name, is_package in pkgutil_iter_modules(
        package.__path__, prefix=package.__name__ + "."
    ):
        mod = import_module(name)
        yield mod, is_package
