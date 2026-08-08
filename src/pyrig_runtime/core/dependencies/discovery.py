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


def subclasses_across_dependencies[T](
    cls: type[T],
    module: ModuleType,
) -> Iterator[type[T]]:
    """Yield subclasses of `cls` found in `module` and its dependents' equivalents.

    The search covers `module` itself, every sub-module if `module` is a
    package, and the equivalently-located module (and its own sub-modules,
    if a package) in every installed package that depends on `module`'s
    root package.

    Args:
        cls: Base class whose subclasses should be discovered.
        module: Module or package that scopes the search, and whose root
            package determines which dependents are searched.

    Yields:
        Subclass types of `cls` found anywhere in the search scope. The
        order is stable across calls but reflects discovery order, not
        any deliberate priority.

    Note:
        Every module within the search scope is imported as a side effect,
        executing any module-level code it contains.
    """
    for package in filter(
        is_package,
        chain(
            (module,),
            equivalent_modules_across_dependencies(module=module),
        ),
    ):
        register_package_modules(package)

    module_name = module.__name__
    root_name = root_module_name(module_name)
    for subclass in discover_subclasses(cls):
        if replace_root_module_name(
            subclass.__module__,
            root_name,
        ).startswith(module_name):
            yield subclass


def equivalent_modules_across_dependencies(
    module: ModuleType,
) -> Iterator[ModuleType]:
    """Yield the equivalent module from every dependent of `module`'s root package.

    For each installed package that depends on the root of `module`,
    locates the module at the same sub-path within that dependent and
    yields it if the import succeeds. The root package itself is excluded
    from results.

    Args:
        module: Module whose root determines which dependents to search
            and whose sub-path within that root locates the corresponding
            module in each dependent.

    Yields:
        Successfully imported module objects, in dependency order.
        Dependents are silently skipped whenever importing the equivalent
        module fails, whether because no module exists at that sub-path
        or because the import itself raises.
    """
    for package in dependent_packages(root_module(module)):
        package_module = replace_root_module(module, package.__name__, default=None)
        if package_module is not None:
            yield package_module


@cache
def dependent_packages(package: ModuleType) -> tuple[ModuleType, ...]:
    """Return every installed package that depends on `package`.

    The result is cached per unique `package` argument.

    Args:
        package: Package whose dependents should be discovered.

    Returns:
        Tuple of imported module objects for every package that depends on
        `package`, directly or transitively, in dependency order
        (dependencies before dependents). Does not include `package`
        itself.

    Raises:
        KeyError: If `package` is not `pyrig_runtime` or one of its
            dependents.
    """
    graph = dependency_graph()
    return tuple(import_modules(graph.sorted_ancestors(package.__name__)))


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
