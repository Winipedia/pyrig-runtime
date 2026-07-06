"""Utilities for Python modules."""

import logging
from collections.abc import Iterable, Iterator
from importlib import import_module
from pkgutil import iter_modules as pkgutil_iter_modules
from types import ModuleType
from typing import Any, overload

from pyrig_runtime.core.constants import MISSING
from pyrig_runtime.core.wrappers import safe_call

logger = logging.getLogger(__name__)


@overload
def replace_root_module(module: ModuleType, root: str) -> ModuleType: ...
@overload
def replace_root_module[T](
    module: ModuleType, root: str, default: T
) -> ModuleType | T: ...
def replace_root_module(
    module: ModuleType, root: str, default: Any = MISSING
) -> ModuleType | Any:
    """Import the equivalent module under a different root package.

    Replaces the first dotted segment of `module`'s name with `root` and
    attempts to import the resulting module name. Later segments are left
    untouched even if they happen to share the old root's name.

    Args:
        module: Module whose root segment should be swapped.
        root: Root package name to substitute in.
        default: Value to return if the import fails. If not provided,
            the exception propagates unchanged.

    Returns:
        The imported module at the equivalent sub-path under `root`, or
        `default` if the import fails and `default` was provided.

    Example:
        >>> from some_package.subpackage import module
        >>> replace_root_module(module, "other_package")
        <module 'other_package.subpackage.module'
         from '/path/to/other_package/subpackage/module.py'>
    """
    return safe_import_module(replace_root_module_name(module, root), default=default)


def replace_root_module_name(module: ModuleType, root: str) -> str:
    """Return the equivalent module name under a different root package.

    Replaces the first dotted segment of `module.__name__` with `root`. Later
    segments are left untouched even if they happen to share the old root's
    name.

    Args:
        module: Module whose root segment should be swapped.
        root: Root package name to substitute in.

    Returns:
        The equivalent dotted module name under `root`.

    Example:
        >>> replace_root_module_name(module, "other_package")
        'other_package.subpackage.module'
    """
    return module.__name__.replace(root_module_name(module), root, 1)


def root_module(module: ModuleType) -> ModuleType:
    """Import and return the top-level package of the given module.

    For a module named `"package.subpackage.module"`, the module corresponding
    to `"package"` is returned. For a top-level module with no dots in its name,
    the module for that same name is returned.

    Args:
        module: Module to resolve the root package for.

    Returns:
        The module corresponding to the first segment of the dotted name.

    Example:
        >>> from some_package.subpackage import module
        >>> root_module(module)
        <module 'some_package' from '/path/to/some_package/__init__.py'>
    """
    return import_module(root_module_name(module))


def root_module_name(module: ModuleType) -> str:
    """Return the name of the top-level package of the given module.

    For a module named `"package.subpackage.module"`, the string `"package"`
    is returned. For a top-level module with no dots in its name, that same
    name is returned.

    Args:
        module: Module to resolve the root package name for.

    Returns:
        The first segment of the dotted module name.

    Example:
        >>> from some_package.subpackage import module
        >>> root_module_name(module)
        'some_package'
    """
    return module.__name__.split(".", 1)[0]


@overload
def safe_import_module(
    module_name: str,
    package: str | None = ...,
    *,
    exceptions: tuple[type[BaseException], ...] = ...,
) -> ModuleType: ...
@overload
def safe_import_module[T](
    module_name: str,
    package: str | None = ...,
    *,
    default: T,
    exceptions: tuple[type[BaseException], ...] = ...,
) -> ModuleType | T: ...
def safe_import_module(
    module_name: str,
    package: str | None = None,
    *,
    default: Any = MISSING,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
) -> ModuleType | Any:
    """Import a module by name, with an optional fallback on failure.

    Any `Exception` raised during import — not just `ImportError` — is
    handled, so errors at module level (e.g., `ValueError` raised on
    import) are also covered.

    Args:
        module_name: Dotted module name (e.g., `"package.subpackage.module"`).
        package: Anchor package for relative imports, forwarded to `import_module`.
        default: Value to return if the import raises. If not provided,
            the exception propagates unchanged.
        exceptions: Tuple of exception types to catch. Defaults to `(Exception,)`.

    Returns:
        The imported module, or `default` if an exception is raised and
        `default` was provided.
    """
    return safe_call(
        import_module,
        module_name,
        package,
        default=default,
        exceptions=exceptions,
    )


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
