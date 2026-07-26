"""Network Graph Analysis service to detect cyclic money movement rings."""

import pandas as pd
import networkx as nx
from typing import Dict, List, Tuple, Optional
from app.utils.logger import get_logger
from app.services.graph_adapter import IGraphAdapter
from app.models.graph_models import GraphNode, GraphEdge, CentralityMetrics

logger = get_logger(__name__)

# A1: Entity type detection — maps entity category to column name candidates
ENTITY_COLUMN_MAP: Dict[str, List[str]] = {
    "ip":       ["ip_address", "login_ip", "source_ip", "ip"],
    "device":   ["device_id", "device_fingerprint", "device"],
    "country":  ["country", "jurisdiction", "country_code"],
    "merchant": ["merchant_id", "merchant_name", "merchant"],
    "email":    ["email", "email_address"],
    "phone":    ["phone", "phone_number", "mobile"],
    "wallet":   ["wallet_id", "crypto_wallet", "wallet"],
}

class GraphAnalyzer:
    """Uses NetworkX to build transaction graphs and calculate network-level risk.
    (Legacy implementation preserved for AMLPipeline compatibility)"""

    def __init__(self):
        pass

    def run(self, clean_dataframe: pd.DataFrame) -> Dict[str, float]:
        """Builds a directed graph and calculates a network risk score for each customer."""
        logger.info("Starting Network Graph Analysis...")
        sender_col = None
        receiver_col = None
        
        for col in clean_dataframe.columns:
            if "sender" in col.lower() or "customer_id" == col.lower():
                if sender_col is None:
                    sender_col = col
            if "receiver" in col.lower() or "recipient" in col.lower() or "dest" in col.lower():
                receiver_col = col
                
        if not sender_col or not receiver_col:
            cust_col = "customer_id" if "customer_id" in clean_dataframe.columns else sender_col
            if cust_col:
                return {str(c): 0.0 for c in clean_dataframe[cust_col].unique()}
            return {}

        if len(clean_dataframe) > 50000:
            df_subset = clean_dataframe.sample(50000, random_state=42)
        else:
            df_subset = clean_dataframe

        if "amount" not in df_subset.columns:
            df_subset["amount"] = 1.0
        
        edges = df_subset.groupby([sender_col, receiver_col]).agg(
            weight=("amount", "sum"),
            count=("amount", "count")
        ).reset_index()

        edges[sender_col] = edges[sender_col].astype(str)
        edges[receiver_col] = edges[receiver_col].astype(str)

        G = nx.from_pandas_edgelist(
            edges, 
            source=sender_col, 
            target=receiver_col, 
            edge_attr=['weight', 'count'], 
            create_using=nx.DiGraph()
        )
                
        risk_scores: Dict[str, float] = {}
        for node in G.nodes():
            score = 0.0
            in_deg = G.in_degree(node)
            out_deg = G.out_degree(node)
            total_deg = in_deg + out_deg
            
            if total_deg > 50:
                score += 10.0
            if out_deg > 10 and in_deg <= 2:
                score += 20.0
            if in_deg > 10 and out_deg <= 2:
                score += 20.0
            score += min(total_deg, 50.0)
            risk_scores[node] = min(score, 100.0)
            
        return risk_scores


class KnowledgeGraphAnalyzer:
    """Executes pure graph theoretical algorithms on the IGraphAdapter for the Knowledge Graph module."""
    
    def __init__(self, adapter: IGraphAdapter):
        self.adapter = adapter
        
    def get_ego_graph(self, node_id: str, radius: int = 2) -> Tuple[List[GraphNode], List[GraphEdge]]:
        """Retrieve the neighborhood graph centered on a specific node."""
        return self.adapter.get_ego_graph_data(node_id, radius)
        
    def calculate_centrality(self, node_id: str) -> CentralityMetrics:
        """Calculate network centrality metrics for a specific node."""
        # Note: In a production enterprise system, centrality might be cached or approximated.
        degree_map = self.adapter.calculate_degree_centrality()
        betweenness_map = self.adapter.calculate_betweenness_centrality(k=50) # Approx for speed
        pagerank_map = self.adapter.calculate_pagerank()
        
        return CentralityMetrics(
            degree=degree_map.get(node_id, 0.0),
            betweenness=betweenness_map.get(node_id, 0.0),
            pagerank=pagerank_map.get(node_id, 0.0)
        )
        
    def find_shortest_path(self, source: str, target: str) -> List[GraphNode]:
        """Find the shortest path between two nodes and return the populated nodes."""
        path_ids = self.adapter.shortest_path(source, target)
        return [self.adapter.get_node(n_id) for n_id in path_ids]
        
    def get_connected_entities(self, node_id: str) -> List[GraphNode]:
        """Get all entities directly connected to the specified node."""
        neighbor_ids = self.adapter.get_neighbors(node_id)
        return [self.adapter.get_node(n_id) for n_id in neighbor_ids]
        
    def get_communities(self) -> List[List[str]]:
        """Detect and return distinct communities within the graph."""
        return self.adapter.detect_communities()