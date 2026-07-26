"""Adapter layer abstracting the underlying graph database/library implementation."""

from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Set
import networkx as nx

from app.models.graph_models import GraphNode, GraphEdge

class IGraphAdapter(ABC):
    """Abstract interface for graph operations, enabling easy swapping of graph backends (e.g., Neo4j, Neptune)."""
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all nodes and edges from the graph."""
        pass
        
    @abstractmethod
    def add_node(self, node: GraphNode) -> None:
        """Add a domain GraphNode to the graph."""
        pass
    
    @abstractmethod
    def add_edge(self, edge: GraphEdge) -> None:
        """Add a domain GraphEdge to the graph."""
        pass
        
    @abstractmethod
    def has_node(self, node_id: str) -> bool:
        """Check if a node exists in the graph."""
        pass
        
    @abstractmethod
    def get_node(self, node_id: str) -> GraphNode:
        """Retrieve a specific node by its ID."""
        pass

    @abstractmethod
    def get_neighbors(self, node_id: str) -> List[str]:
        """Get all node IDs connected to the specified node."""
        pass

    @abstractmethod
    def get_ego_graph_data(self, node_id: str, radius: int) -> Tuple[List[GraphNode], List[GraphEdge]]:
        """Retrieve all nodes and edges within a specified radius of a focal node."""
        pass

    @abstractmethod
    def calculate_degree_centrality(self) -> Dict[str, float]:
        """Calculate degree centrality for all nodes."""
        pass

    @abstractmethod
    def calculate_betweenness_centrality(self, k: int = None) -> Dict[str, float]:
        """Calculate betweenness centrality, optionally approximated by k nodes."""
        pass

    @abstractmethod
    def calculate_pagerank(self) -> Dict[str, float]:
        """Calculate PageRank for all nodes."""
        pass

    @abstractmethod
    def detect_communities(self) -> List[List[str]]:
        """Detect communities (clusters) of nodes in the graph."""
        pass

    @abstractmethod
    def shortest_path(self, source: str, target: str) -> List[str]:
        """Find the shortest path between two nodes."""
        pass


class NetworkXAdapter(IGraphAdapter):
    """In-memory NetworkX implementation of the Graph Adapter."""
    
    def __init__(self):
        self._graph = nx.DiGraph()
        self._clear_cache()

    def _clear_cache(self) -> None:
        self._degree_cache = None
        self._betweenness_cache = None
        self._pagerank_cache = None
        self._communities_cache = None

    def clear(self) -> None:
        self._graph.clear()
        self._clear_cache()

    def add_node(self, node: GraphNode) -> None:
        self._graph.add_node(
            node.id, 
            label=node.label, 
            type=node.type, 
            metadata=node.metadata
        )

    def add_edge(self, edge: GraphEdge) -> None:
        self._graph.add_edge(
            edge.source, 
            edge.target, 
            relationship=edge.relationship, 
            weight=edge.weight, 
            timestamp=edge.timestamp,
            metadata=edge.metadata
        )
        
    def has_node(self, node_id: str) -> bool:
        return self._graph.has_node(node_id)
        
    def get_node(self, node_id: str) -> GraphNode:
        if not self.has_node(node_id):
            raise KeyError(f"Node {node_id} not found in graph.")
        data = self._graph.nodes[node_id]
        return GraphNode(
            id=node_id,
            label=data.get("label", node_id),
            type=data.get("type", "UNKNOWN"),
            metadata=data.get("metadata", {})
        )

    def get_neighbors(self, node_id: str) -> List[str]:
        if not self.has_node(node_id):
            return []
        # For directed graphs, combine successors and predecessors for undirected neighborhood
        neighbors = set(self._graph.successors(node_id)).union(set(self._graph.predecessors(node_id)))
        return list(neighbors)

    def _extract_nodes_and_edges(self, sub_g: nx.DiGraph) -> Tuple[List[GraphNode], List[GraphEdge]]:
        nodes = []
        for n, data in sub_g.nodes(data=True):
            nodes.append(GraphNode(
                id=n,
                label=data.get("label", str(n)),
                type=data.get("type", "UNKNOWN"),
                metadata=data.get("metadata", {})
            ))
            
        edges = []
        for u, v, data in sub_g.edges(data=True):
            edges.append(GraphEdge(
                source=u,
                target=v,
                relationship=data.get("relationship", "UNKNOWN"),
                weight=data.get("weight", 1.0),
                timestamp=data.get("timestamp"),
                metadata=data.get("metadata", {})
            ))
            
        return nodes, edges

    def get_ego_graph_data(self, node_id: str, radius: int) -> Tuple[List[GraphNode], List[GraphEdge]]:
        if not self.has_node(node_id):
            return [], []
            
        # nx.ego_graph works on directed graphs by following out-edges by default, 
        # to get both directions we use the undirected representation
        undirected_g = self._graph.to_undirected(as_view=True)
        sub_g_undirected = nx.ego_graph(undirected_g, node_id, radius=radius)
        
        # Now extract the original directed edges that are within this subgraph
        sub_g_directed = self._graph.subgraph(sub_g_undirected.nodes)
        
        return self._extract_nodes_and_edges(sub_g_directed)

    def calculate_degree_centrality(self) -> Dict[str, float]:
        if len(self._graph) == 0:
            return {}
        if self._degree_cache is None:
            self._degree_cache = nx.degree_centrality(self._graph)
        return self._degree_cache

    def calculate_betweenness_centrality(self, k: int = 50) -> Dict[str, float]:
        if len(self._graph) == 0:
            return {}
        if self._betweenness_cache is None:
            k_val = min(k, len(self._graph)) if k else None
            self._betweenness_cache = nx.betweenness_centrality(self._graph, k=k_val)
        return self._betweenness_cache

    def calculate_pagerank(self) -> Dict[str, float]:
        if len(self._graph) == 0:
            return {}
        if self._pagerank_cache is None:
            self._pagerank_cache = nx.pagerank(self._graph, alpha=0.85)
        return self._pagerank_cache

    def detect_communities(self) -> List[List[str]]:
        if len(self._graph) == 0:
            return []
        if self._communities_cache is not None:
            return self._communities_cache
        try:
            import networkx.algorithms.community as nx_comm
            undirected_g = self._graph.to_undirected(as_view=True)
            communities = nx_comm.louvain_communities(undirected_g, seed=42)
            self._communities_cache = [list(c) for c in communities]
            return self._communities_cache
        except Exception:
            # Fallback if louvain is not available/fails
            return []

    def shortest_path(self, source: str, target: str) -> List[str]:
        try:
            # Use undirected graph to find path regardless of transaction direction
            undirected_g = self._graph.to_undirected(as_view=True)
            return nx.shortest_path(undirected_g, source=source, target=target)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []
