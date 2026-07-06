"""Abstract directed graph foundation with forward and reverse edge traversal."""

import heapq
from abc import ABC, abstractmethod
from collections import deque
from functools import cache
from typing import Any, Self


class DiGraph(ABC):
    """Abstract directed graph with forward and reverse adjacency tracking.

    Subclasses implement `build` to populate nodes and edges. When a `root`
    node is given, the graph is pruned to contain only that node and every node
    that transitively points to it.

    Attributes:
        root: The root node passed at construction, or `None` if none was given.
        nodes: Set of all node identifiers currently in the graph.
        edges: Forward adjacency map from each node to its outgoing neighbors.
        reverse_edges: Reverse adjacency map from each node to its incoming neighbors.
    """

    @classmethod
    @cache
    def cached(cls, *args: Any, **kwargs: Any) -> Self:
        """Return a cached instance, constructing it only on the first call.

        Repeated calls with identical arguments return the same instance
        without rebuilding the graph.

        Args:
            *args: Positional arguments forwarded to the constructor.
            **kwargs: Keyword arguments forwarded to the constructor.

        Returns:
            The cached graph instance for the given arguments.
        """
        return cls(*args, **kwargs)

    def __init__(self, root: str | None = None) -> None:
        """Initialize the directed graph, optionally pruned to the given root."""
        self.root = root
        self.nodes: set[str] = set()
        self.edges: dict[str, set[str]] = {}
        self.reverse_edges: dict[str, set[str]] = {}
        self.build()
        if self.root is not None:
            self.prune(self.root)

    @abstractmethod
    def build(self) -> None:
        """Populate the graph with nodes and edges.

        Called during construction before any pruning occurs. Subclasses
        must add all nodes and edges that belong to the graph.
        """

    def prune(self, root: str) -> None:
        """Retain only the given root and its ancestors, removing all other nodes.

        Keeps `root` and all its ancestors (nodes with a directed path to
        `root`). All other nodes and their associated edges are removed.

        Args:
            root: The node to keep, along with all nodes that have a directed
                path to it.
        """
        keep = self.ancestors(root) | {root}
        self.nodes = keep
        self.edges = {n: self.edges[n] & keep for n in keep}
        self.reverse_edges = {n: self.reverse_edges[n] & keep for n in keep}

    def add_edge(self, source: str, target: str) -> None:
        """Add a directed edge from source to target.

        Creates both nodes if they do not already exist.

        Args:
            source: Edge origin node.
            target: Edge destination node.
        """
        self.add_node(source)
        self.add_node(target)
        self.edges[source].add(target)
        self.reverse_edges[target].add(source)

    def add_node(self, node: str) -> None:
        """Add a node to the graph. No-op if the node already exists."""
        self.nodes.add(node)
        if node not in self.edges:
            self.edges[node] = set()
        if node not in self.reverse_edges:
            self.reverse_edges[node] = set()

    def sorted_ancestors(self, target: str) -> list[str]:
        """Return all ancestors of the target node in topological order.

        Ancestors are nodes that have a directed path to the target. The
        result is ordered so that each ancestor appears after all ancestors
        it has outgoing edges to.

        Args:
            target: Node to find ancestors of.

        Returns:
            List of ancestor node identifiers in topological order.
            Returns an empty list if the target has no ancestors.

        Raises:
            KeyError: If the target node is not in the graph.
            RuntimeError: If the ancestor subgraph contains a cycle, making
                topological sorting impossible.
        """
        return self.topological_sort_subgraph(self.ancestors(target))

    def ancestors(self, target: str) -> set[str]:
        """Find all nodes that have a directed path to the target node.

        The target itself is excluded from the result.

        Args:
            target: Node to find ancestors for.

        Returns:
            Set of all nodes with a directed path to the target, excluding the
            target itself.

        Raises:
            KeyError: If the target node is not in the graph.
        """
        visited: set[str] = set()
        queue: deque[str] = deque(self.reverse_edges[target])

        while queue:
            node = queue.popleft()
            if node not in visited:
                visited.add(node)
                for neighbor in self.reverse_edges[node]:
                    if neighbor not in visited:
                        queue.append(neighbor)

        return visited

    def topological_sort_subgraph(self, nodes: set[str]) -> list[str]:
        """Sort a subset of nodes in topological order.

        If there is an edge from A to B, B appears before A in the result.
        The ordering is deterministic: when multiple nodes are eligible to be
        emitted at the same step, they are emitted in ascending lexicographic
        order.

        Only edges whose both endpoints are in `nodes` are considered; edges
        to or from nodes outside the subset are ignored.

        Args:
            nodes: The subset of nodes to sort.

        Returns:
            List of nodes in topological order, with each node appearing
            after all nodes it has outgoing edges to.

        Raises:
            RuntimeError: If the subgraph contains a cycle, making topological
                sorting impossible.
        """
        out_degree: dict[str, int] = dict.fromkeys(nodes, 0)

        for node in nodes:
            for dependency in self.edges[node]:
                if dependency in nodes:
                    out_degree[node] += 1

        heap: list[str] = [node for node in nodes if out_degree[node] == 0]
        heapq.heapify(heap)
        result: list[str] = []

        while heap:
            node = heapq.heappop(heap)
            result.append(node)

            for dependent in self.reverse_edges[node]:
                if dependent in nodes:
                    out_degree[dependent] -= 1
                    if out_degree[dependent] == 0:
                        heapq.heappush(heap, dependent)

        if len(result) != len(nodes):
            msg = (
                "Graph contains a cycle; topological sort not possible. "
                "This indicates a circular dependency among the following nodes: "
                f"{set(nodes) - set(result)}"
            )
            raise RuntimeError(msg)

        return result
