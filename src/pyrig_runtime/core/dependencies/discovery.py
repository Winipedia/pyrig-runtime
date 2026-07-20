"""Subclass and module discovery scoped across installed package dependents."""

from collections.abc import Iterator
from functools import cache
from itertools import chain
from types import ModuleType

import pyrig_runtime
from pyrig_runtime.core.dependencies.graph import DependencyGraph
from pyrig_runtime.core.introspection.classes import discover_subclasses
from pyrig_runtime.core.introspection.modules import (
    import_modules,
    replace_root_module,
    replace_root_module_name,
    root_module,
    root_module_name,
)
from pyrig_runtime.core.introspection.packages import (
    is_package,
    register_package_modules,
)


def discover_subclasses_across_dependencies[T](
    cls: type[T],
    module: ModuleType,
) -> Iterator[type[T]]:
    """Yield subclasses of `cls` found in `module` and in dependent packages.

    Args:
        cls: Base class whose subclasses should be discovered.
        module: Module to search first, also used to determine which root
            package to scan for dependents.

    Yields:
        Subclass types of `cls`, with `module` searched first, then
        dependent packages in dependency order.
    """
    for package in filter(
        is_package,
        chain(
            (module,),
            discover_equivalent_modules_across_dependencies(module=module),
        ),
    ):
        register_package_modules(package)

    module_name = module.__name__
    root_name = root_module_name(module_name)
    for subclass in discover_subclasses(cls):
        if replace_root_module_name(
            subclass.__module__,
            root_name,
        ).startswith(
            module_name,
        ):
            yield subclass


def discover_equivalent_modules_across_dependencies(
    module: ModuleType,
) -> Iterator[ModuleType]:
    """Yield the equivalent module from every dependent of `module`'s root package.

    For each installed package that depends on the root of `module`, locates
    the module at the same sub-path within that dependent and yields it if
    it can be imported. The root package itself is excluded from results.

    Args:
        module: Module whose root determines which dependents to search and
            whose sub-path within that root is used to locate the corresponding
            module in each dependent.

    Yields:
        Successfully imported module objects in dependency order. Dependents
        that have no module at the equivalent sub-path are silently skipped.
    """
    for package in dependency_ancestors(root_module(module)):
        package_module = replace_root_module(module, package.__name__, default=None)
        if package_module is not None:
            yield package_module


@cache
def dependency_ancestors(target: ModuleType) -> tuple[ModuleType, ...]:
    """Return every installed package that depends on `target`.

    The result is cached per unique `target` argument.

    Args:
        target: Package whose dependents should be discovered.

    Returns:
        Tuple of imported module objects for every package that depends on
        `target` directly or transitively, in dependency order. Does not
        include `target` itself.

    Raises:
        KeyError: If `target` is not `pyrig_runtime` or one of its
            dependents.
    """
    graph = dependency_graph()
    return tuple(import_modules(graph.sorted_ancestors(target.__name__)))


@cache
def dependency_graph() -> DependencyGraph:
    """Return the dependency graph of `pyrig_runtime` and its dependents.

    Built once and cached. Pruned to `pyrig_runtime` and every package that
    depends on it, directly or transitively; packages it depends on are not
    included.

    Returns:
        Directed graph rooted at `pyrig_runtime`, containing only its
        ancestors.

    Note:
        The returned instance is shared across all callers. Do not mutate it.
    """
    graph = DependencyGraph()
    graph.prune(root=pyrig_runtime.__name__)
    return graph
