"""Abstract directed graph foundation with forward and reverse edge traversal."""

import heapq
from abc import ABC, abstractmethod
from collections import deque


class DiGraph(ABC):
    """Abstract directed graph with forward and reverse adjacency tracking.

    Subclasses implement `build` to populate nodes and edges.

    Attributes:
        nodes: Set of all node identifiers currently in the graph.
        edges: Forward adjacency map from each node to its outgoing neighbors.
        reverse_edges: Reverse adjacency map from each node to its incoming neighbors.
    """

    def __init__(self) -> None:
        """Initialize the directed graph by building it."""
        self.nodes: set[str] = set()
        self.edges: dict[str, set[str]] = {}
        self.reverse_edges: dict[str, set[str]] = {}
        self.build()

    @abstractmethod
    def build(self) -> None:
        """Populate the graph with nodes and edges.

        Called during construction. Subclasses must add every node and edge
        that belongs to the graph.
        """

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
        if node not in self.nodes:
            self.nodes.add(node)
            self.edges[node] = set()
            self.reverse_edges[node] = set()

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
            KeyError: If any node in `nodes` is not part of the graph.
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
            msg = f"graph contains a cycle among: {set(nodes) - set(result)}"
            raise RuntimeError(msg)

        return result

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
        visited: set[str] = set(self.reverse_edges[target])
        queue: deque[str] = deque(visited)

        while queue:
            node = queue.popleft()
            for neighbor in self.reverse_edges[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return visited
