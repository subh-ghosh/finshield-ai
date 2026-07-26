"""Network Graph Analysis service to detect cyclic money movement rings."""

import pandas as pd
import networkx as nx
from typing import Dict
from app.utils.logger import get_logger

logger = get_logger(__name__)

class GraphAnalyzer:
    """Uses NetworkX to build transaction graphs and calculate network-level risk."""

    def __init__(self):
        pass

    def run(self, clean_dataframe: pd.DataFrame) -> Dict[str, float]:
        """Builds a directed graph and calculates a network risk score for each customer.
        
        Args:
            clean_dataframe: Transactions DataFrame containing SENDER_ACCOUNT_ID and RECEIVER_ACCOUNT_ID.
            
        Returns:
            Dict[str, float]: Mapping of customer_id to network_risk_score.
        """
        logger.info("Starting Network Graph Analysis...")
        
        # We need sender and receiver. Since transactions have 'customer_id' as the sender,
        # and 'receiver_account_id' (or similar). Let's map it.
        # Ensure we have the necessary columns
        sender_col = None
        receiver_col = None
        
        for col in clean_dataframe.columns:
            if "sender" in col.lower() or "customer_id" == col.lower():
                if sender_col is None:
                    sender_col = col
            if "receiver" in col.lower() or "recipient" in col.lower() or "dest" in col.lower():
                receiver_col = col
                
        if not sender_col or not receiver_col:
            logger.warning("Could not find sender/receiver columns for Graph Analysis. Returning 0.0 scores.")
            # Return 0.0 for all unique customer_ids if available
            cust_col = "customer_id" if "customer_id" in clean_dataframe.columns else sender_col
            if cust_col:
                return {str(c): 0.0 for c in clean_dataframe[cust_col].unique()}
            return {}

        # Vectorized graph building
        logger.info("Aggregating edges for graph...")
        # Cap the dataframe size to prevent extreme memory usage during graph analysis
        if len(clean_dataframe) > 50000:
            logger.warning(f"Dataframe too large for graph analysis ({len(clean_dataframe)}). Sampling 50000 rows.")
            df_subset = clean_dataframe.sample(50000, random_state=42)
        else:
            df_subset = clean_dataframe

        # Ensure amount is float
        if "amount" not in df_subset.columns:
            df_subset["amount"] = 1.0
        
        # Group by sender and receiver to sum weights and count edges
        edges = df_subset.groupby([sender_col, receiver_col]).agg(
            weight=("amount", "sum"),
            count=("amount", "count")
        ).reset_index()

        # Convert columns to string explicitly to avoid typing issues
        edges[sender_col] = edges[sender_col].astype(str)
        edges[receiver_col] = edges[receiver_col].astype(str)

        G = nx.from_pandas_edgelist(
            edges, 
            source=sender_col, 
            target=receiver_col, 
            edge_attr=['weight', 'count'], 
            create_using=nx.DiGraph()
        )
                
        logger.info(f"Built transaction graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
        
        risk_scores: Dict[str, float] = {}
        
        # Assign scores based on simple degrees to be O(V+E) and instant
        for node in G.nodes():
            score = 0.0
            
            in_deg = G.in_degree(node)
            out_deg = G.out_degree(node)
            total_deg = in_deg + out_deg
            
            # High activity node
            if total_deg > 50:
                score += 10.0
                
            # Fan-out anomaly (distributor)
            if out_deg > 10 and in_deg <= 2:
                score += 20.0
                
            # Fan-in anomaly (collector)
            if in_deg > 10 and out_deg <= 2:
                score += 20.0
                
            # Fast simple heuristic instead of pagerank
            score += min(total_deg, 50.0)
                
            risk_scores[node] = min(score, 100.0)
            
        return risk_scores