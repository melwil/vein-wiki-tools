from __future__ import annotations

import logging
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Generic, TypeVar, cast

from vein_wiki_tools.clients.pakdump.models import N, UEModel
from vein_wiki_tools.errors import VeinError
from vein_wiki_tools.models.common import Link, LinkType

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class Graph:
    root_node: Node | None = field(default=None)
    nodes: dict[str, Node] = field(default_factory=dict)
    links: list[Link] = field(default_factory=list)

    deleted_nodes: dict[str, Node] = field(default_factory=dict)
    # deleted_links = ...

    aliases: dict[str, str] = field(default_factory=dict)

    def walk(
        self,
        start_node: Node[N] | None = None,
        allowed_link_types: set[LinkType] = set(),
    ) -> Iterator[Node]:
        """
        Walk the graph in a Breadth First Search (BFS).
        Starting at start_node, and following outgoing links (edges) that are
        in the allowed_links list.

        Args:
            start_node (Node[N]): a Node object. ``Default = root node``
            allowed_link_types (N): any covariant type of UEModel. ``Default = all``

        Yield:
            ``Node[N]`` is a Node object with unknown N type
        """
        if start_node is None:
            if self.root_node is None:
                raise ValueError("Graph has no root node and no start node was supplied")
            start_node = self.root_node
        if len(allowed_link_types) == 0:
            allowed_link_types = set(LinkType)
        node_stack: list[Node] = [start_node]
        visited: list[str] = []
        current: Node[UEModel]
        while len(node_stack):
            current = node_stack.pop(0)
            yield current
            visited.append(current.id)
            for link_type, node in current.edges:
                if link_type in allowed_link_types and node.id not in visited:
                    node_stack.append(node)

    def upsert(self, ue_model: N, update: bool = False) -> Node[N]:
        if not ue_model.get_object_name():
            raise AttributeError("UEModel missing name [ue_model=%s]", ue_model)

        # Create new Node
        if ue_model.get_object_name() not in self.nodes:
            node = Node(ue_model=ue_model)
            self.nodes[ue_model.get_object_name()] = node
            return node

        # Update UEModel in existing Node
        node = self.nodes[ue_model.get_object_name()]
        if not update:
            raise ValueError(
                "UEModel with name already present [existing=%s, upserting=%s]",
                node.ue_model,
                ue_model,
            )
        if type(node.ue_model) is not type(ue_model):
            raise ValueError(
                "Attempted to replace UEModel in Node with another type [existing=%s, upserting=%s]",
                node.ue_model,
                ue_model,
            )
        node.ue_model = ue_model
        return node

    def update(self, ue_models: list[UEModel]):
        for ue_model in ue_models:
            self.upsert(ue_model=ue_model, update=True)

    def add_node(self, node: Node[N]) -> Node[N]:
        if self.nodes.get(node.ue_model.get_object_name()):
            logger.debug(
                "Attempted to add UEModel in Node with existing key. Skipped. [key=%s]",
                node.ue_model.get_object_name(),
            )

        self.nodes[node.ue_model.get_object_name()] = node
        for _, neighbour in node.edges:
            self.add_node(neighbour)

        return node

    def get_node(self, key: str | None, ue_model_type: type[N]) -> Node[N] | None:
        """
        Get a ue_model from the graph.

        Args:
            key (str): external_reference or name for the ue_model can
            both be used as keys.
            ue_model_type (N): any covariant type of UEModel

        Return:
            ``Node[N]`` is a Node object with a reference to the ue_model of type N
        """
        if key is None:
            raise VeinError("Key cannot be None")

        node = self.nodes.get(key)
        if node is None and key in self.aliases:
            node = self.nodes.get(self.aliases[key])
        if node is None:
            return None
        # if isinstance(node.ue_model, ue_model_type):
        if type(node.ue_model) is not ue_model_type:
            logger.warning(
                "UEModel found at key had wrong type [key=%s,ue_model_type=%s,actual_type=%s]",
                key,
                ue_model_type,
                type(node.ue_model),
            )
            return None

        node = cast(Node[N], node)
        return node

    def delete_node(self, node: Node) -> None:
        self.deleted_nodes[node.ue_model.get_interface_name()] = node
        # Delete links up from this node (neighbours)
        for link_type, edge_node in node.edges:
            edge_node.neighbours.remove((link_type, node))
        # Delete links down from this node (edges)
        for link_type, neighbour_node in node.neighbours:
            neighbour_node.edges.remove((link_type, node))
        del self.nodes[node.ue_model.get_interface_name()]

    def save(self) -> list:
        ue_models = list()
        for n in self.nodes.values():
            ue_model = n.save()
            if ue_model is not None:
                ue_models.append(ue_model)
        return ue_models

    def save_links(self) -> list[Link]:
        links: list[Link] = []
        for link in self.links:
            # link.skip_state = True
            links.append(link)
        return links

    # We declare our own repr because in sufficiently large graphs, the default repr is way too slow
    def __repr__(self) -> str:
        return f"Graph(nodes={len(self.nodes)}, links={len(self.links)})"


T = TypeVar("T", bound=UEModel)


@dataclass(slots=True)
class Node(Generic[T]):
    id: str
    _ue_model: T
    # Neighbours is just for backwards references
    neighbours: list[tuple[LinkType, Node]]
    # Edges are actual links (relationships) we want to add to the db
    edges: list[tuple[LinkType, Node]]
    modified: bool
    topological_order: int

    def __init__(self, ue_model: T, topological_order: int = 0) -> None:
        if not isinstance(ue_model, UEModel):
            raise TypeError("UEModel must be of type UEModel")
        self.id = ue_model.get_object_name()
        self._ue_model = ue_model
        self.neighbours = list()
        self.edges = list()
        self.modified = True
        self.topological_order = topological_order

    @property
    def ue_model(self) -> T:
        return self._ue_model

    @ue_model.setter
    def ue_model(self, ue_model: T) -> None:
        self._ue_model = ue_model
        self.modified = True

    def add_edge(self, link_type: LinkType, node: Node[N]) -> None:
        """
        Add link ``self``-[:``link_type``]->``node``
        """
        self.edges.append((link_type, node))
        node.neighbours.append((link_type, self))

    def remove_edge(self, link_type: LinkType, node: Node[N]) -> None:
        self.edges.remove((link_type, node))
        node.neighbours.remove((link_type, self))

    def save(self) -> T | None:
        if self.modified:
            # We do not want to store states during import
            # self.ue_model.skip_state = True
            return self._ue_model
        return None

    def update(self, ue_model: T) -> None:
        self._ue_model = ue_model
        self.modified = False

    # We declare our own repr because in sufficiently large graphs, the default repr is way too slow
    def __repr__(self) -> str:
        return f"Node(ue_model.type={type(self.ue_model)}, edges={len(self.edges)})"
