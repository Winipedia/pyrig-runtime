"""Test module."""

import importlib.metadata

from pyrig_runtime.core.dependencies.graph import DependencyGraph

DEP_GRAPH = DependencyGraph()


class TestDependencyGraph:
    """Test class."""

    def test_parse_name_and_deps(self) -> None:
        """Test method."""
        name = "pyrig"
        dist = importlib.metadata.distribution(name)
        result_name, result_deps = DEP_GRAPH.parse_name_and_deps(dist)
        assert result_name == "pyrig"
        assert "typer" in result_deps

    def test_build(self) -> None:
        """Test method."""
        assert len(DEP_GRAPH.nodes) > 0
        assert "" not in DEP_GRAPH.nodes
        # Verify that known packages are in the graph
        assert "pyrig" in DEP_GRAPH.nodes
        assert "typer" in DEP_GRAPH.nodes
        assert "requests" in DEP_GRAPH.nodes
        assert "nonexistent_package" not in DEP_GRAPH.nodes
