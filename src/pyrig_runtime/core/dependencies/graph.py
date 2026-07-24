"""Directed graph of installed Python package dependency relationships."""

import importlib.metadata
from collections.abc import Iterator

from pyrig_runtime.core.dependencies.distribution import (
    distribution_header,
    distribution_metadata,
    distribution_name,
    distribution_requirement_as_module_name,
    distribution_requirements,
)
from pyrig_runtime.core.graph import DiGraph
from pyrig_runtime.core.strings import (
    kebab_to_snake_case,
)


class DependencyGraph(DiGraph):
    """Directed graph of installed Python package dependencies.

    Nodes are package names normalized to their importable module form
    (hyphens become underscores); an edge A → B means "A depends on B".
    The graph is built at instantiation by scanning every installed
    distribution.
    """

    def build(self) -> None:
        """Build the graph from installed Python distributions.

        Distributions whose metadata cannot be read are skipped and do
        not become nodes.
        """
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

        The name and every dependency name are normalized to an importable
        module name; dots are preserved for namespace packages (e.g.
        `zope.interface` remains `zope.interface`).

        Args:
            dist: Distribution to extract metadata from.

        Returns:
            A two-tuple `(name, deps)` where `deps` is an iterator over the
            normalized name of each dependency the distribution declares. If
            the distribution's metadata cannot be read, `name` is the empty
            string and `deps` yields nothing.

        Raises:
            LookupError: If the distribution's metadata can be read but does
                not declare a `Name` field.
        """
        metadata = distribution_metadata(dist)
        if metadata is None:
            return "", iter(())
        header = distribution_header(metadata)
        return kebab_to_snake_case(distribution_name(header)), (
            distribution_requirement_as_module_name(req)
            for req in distribution_requirements(header)
        )
