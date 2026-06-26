"""Python module utilities."""

import logging
from collections.abc import Iterable, Iterator
from importlib import import_module
from pkgutil import iter_modules as pkgutil_iter_modules
from types import ModuleType
from typing import Any

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


def import_module_with_default(
    module_name: str, default: Any = None
) -> ModuleType | Any:
    """Import a module by name, returning a default value on failure.

    Any `Exception` raised during import — not just `ImportError` — triggers
    the fallback, so errors at module level (e.g., `ValueError` raised on
    import) are also caught.

    Args:
        module_name: Dotted module name (e.g., `"package.subpackage.module"`).
        default: Value to return if the import raises. Defaults to `None`.

    Returns:
        The imported module, or `default` if any exception is raised.
    """
    try:
        return import_module(module_name)
    except Exception as e:  # noqa: BLE001
        logger.debug(
            "Could not import module %s, returning default value %s. Exception: %s",
            module_name,
            default,
            e,
        )
        return default


def replace_root_module_name(module: ModuleType, root_module_name: str) -> str:
    """Replace the root package segment in a module's fully qualified name.

    Only the first segment is replaced; later segments are left untouched even
    if they happen to share the old root's name. Useful for mapping modules
    between parallel package hierarchies (e.g., source modules to their test
    equivalents).

    Args:
        module: Module whose name to transform.
        root_module_name: Root package name to substitute in.

    Returns:
        The module name with its first dotted segment replaced.

    Example:
        >>> from types import ModuleType
        >>> mod = ModuleType("pyrig.rig.configs.base")
        >>> replace_root_module_name(mod, "my_project")
        'my_project.rig.configs.base'
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
        Importing each child is a deliberate side effect — it causes subclasses
        defined in those modules to register with the interpreter, enabling
        class-discovery mechanisms that rely on `__subclasses__()`.
    """
    for _finder, name, is_package in pkgutil_iter_modules(
        package.__path__, prefix=package.__name__ + "."
    ):
        mod = import_module(name)
        yield mod, is_package
