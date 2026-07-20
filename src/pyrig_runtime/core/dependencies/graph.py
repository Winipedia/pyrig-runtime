"""Directed graph of installed Python package dependency relationships."""

import importlib.metadata
from collections.abc import Iterator

from pyrig_runtime.core.graph import DiGraph
from pyrig_runtime.core.strings import (
    dependency_requirement_as_module_name,
    distribution_header,
    distribution_header_value_pattern,
    kebab_to_snake_case,
)

DISTRIBUTION_NAME_PATTERN = distribution_header_value_pattern("Name")
DISTRIBUTION_REQUIRES_DIST_PATTERN = distribution_header_value_pattern("Requires-Dist")


class DependencyGraph(DiGraph):
    """Directed graph of installed Python package dependencies.

    Nodes are package names; an edge A → B means "A depends on B".
    The graph is built at instantiation by scanning all installed
    distributions.
    """

    def build(self) -> None:
        """Build the graph from installed Python distributions."""
        for dist in importlib.metadata.distributions():
            name, deps = self.parse_name_and_deps(dist)
            if not name:
                continue
            self.add_node(name)
            for dep in deps:
                self.add_edge(name, dep)

    def parse_name_and_deps(
        self,
        dist: importlib.metadata.Distribution,
    ) -> tuple[str, Iterator[str]]:
        """Extract the package name and dependencies from a distribution.

        Both the package name and every dependency name are normalized to an
        importable module name; version specifiers and extras in requirement
        strings are stripped. Dots are preserved for namespace packages
        (e.g. `zope.interface` remains `zope.interface`). The dependency
        iterator is exhausted once consumed; it yields nothing when the
        distribution declares no dependencies.

        Args:
            dist: Distribution to extract metadata from.

        Returns:
            A two-tuple `(name, deps)` where `name` is the normalized package
            name and `deps` is an iterator over the normalized name of each
            declared dependency.

        Note:
            This does not support legacy distributions that do not declare a
            `Requires-Dist` field in their metadata.
            Such distributions will be treated as having no dependencies.
        """
        header = distribution_header(dist)
        if not header:
            return "", iter(())
        return kebab_to_snake_case(DISTRIBUTION_NAME_PATTERN.findall(header)[0]), (
            dependency_requirement_as_module_name(req)
            for req in DISTRIBUTION_REQUIRES_DIST_PATTERN.findall(header)
        )
