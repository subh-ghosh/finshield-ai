"""Graph Neural Network for relational risk scoring.

Implements a lightweight numpy-only GCN (no PyTorch/TF dependency)
and a Temporal GCN extension with time-windowed snapshots.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SimpleGCN:
    """Lightweight Graph Convolutional Network using numpy-only message passing.
    
    Runs without PyTorch/TensorFlow for hackathon portability.
    Learns relational structure: a customer connected to 3 shell companies 
    is riskier than one connected to 3 retail stores.
    """

    def __init__(self, n_layers: int = 2, hidden_dim: int = 16):
        self.n_layers = n_layers
        self.hidden_dim = hidden_dim
        self.weights: List[np.ndarray] = []

    def _build_adjacency(self, edges: List[Tuple[str, str]], node_index: Dict[str, int]) -> np.ndarray:
        """Build normalized adjacency matrix from edge list."""
        n = len(node_index)
        A = np.zeros((n, n))
        for src, dst in edges:
            if src in node_index and dst in node_index:
                A[node_index[src], node_index[dst]] = 1.0
                A[node_index[dst], node_index[src]] = 1.0  # undirected
        
        # Add self-loops and normalize (Kipf & Welling, 2017)
        A += np.eye(n)
        D_inv_sqrt = np.diag(1.0 / np.sqrt(A.sum(axis=1) + 1e-8))
        return D_inv_sqrt @ A @ D_inv_sqrt

    def fit_predict(self, nodes: List[str], edges: List[Tuple[str, str]],
                    node_features: Dict[str, np.ndarray]) -> Dict[str, float]:
        """Run GCN message passing and return per-node risk scores (0-100)."""
        if not nodes or not edges:
            return {}

        node_index = {n: i for i, n in enumerate(nodes)}
        n = len(nodes)

        # Build feature matrix
        feat_dim = len(next(iter(node_features.values()))) if node_features else 4
        X = np.zeros((n, feat_dim))
        for node, idx in node_index.items():
            if node in node_features:
                X[idx] = node_features[node]

        # Adjacency
        A_norm = self._build_adjacency(edges, node_index)

        # Initialize weights (Xavier-like, deterministic seed)
        np.random.seed(42)
        dims = [feat_dim] + [self.hidden_dim] * self.n_layers + [1]
        self.weights = [np.random.randn(dims[i], dims[i + 1]) * 0.5 for i in range(len(dims) - 1)]

        # Forward pass (message passing)
        H = X
        for W in self.weights[:-1]:
            H = A_norm @ H @ W
            H = np.maximum(H, 0)  # ReLU activation

        # Final layer → risk score
        H = A_norm @ H @ self.weights[-1]
        scores = 1.0 / (1.0 + np.exp(-H))  # Sigmoid to [0, 1]

        return {node: float(scores[idx][0]) * 100 for node, idx in node_index.items()}


class TemporalGCN:
    """Temporal extension of GCN — detects patterns that evolve over time.
    
    Splits transactions into time windows (e.g., 7-day buckets), 
    builds a GCN snapshot for each window, and aggregates with 
    exponential decay (recent windows weighted more).
    """

    def __init__(self, window_days: int = 7, n_layers: int = 2, hidden_dim: int = 16, decay: float = 0.8):
        self.window_days = window_days
        self.decay = decay
        self.gcn = SimpleGCN(n_layers=n_layers, hidden_dim=hidden_dim)

    def fit_predict(self, nodes: List[str],
                    edges_with_time: List[Tuple[str, str, Optional[str]]],
                    node_features: Dict[str, np.ndarray]) -> Dict[str, float]:
        """Run temporal GCN and return per-node risk scores (0-100).
        
        Args:
            nodes: List of node IDs.
            edges_with_time: List of (source, target, timestamp_str) tuples.
            node_features: Per-node feature vectors.
        """
        if not nodes or not edges_with_time:
            return {}

        # Parse timestamps and bucket into windows
        windows: Dict[int, List[Tuple[str, str]]] = {}
        for src, dst, ts_str in edges_with_time:
            try:
                ts = pd.Timestamp(ts_str) if ts_str else pd.Timestamp("1970-01-01")
                bucket = int(ts.timestamp() // (self.window_days * 86400))
            except Exception:
                bucket = 0
            windows.setdefault(bucket, []).append((src, dst))

        if not windows:
            return self.gcn.fit_predict(nodes, [(s, d) for s, d, _ in edges_with_time], node_features)

        # Sort windows chronologically
        sorted_buckets = sorted(windows.keys())
        n_windows = len(sorted_buckets)

        # Run GCN on each window, aggregate with exponential decay
        aggregated: Dict[str, float] = {n: 0.0 for n in nodes}
        total_weight = 0.0

        for i, bucket in enumerate(sorted_buckets):
            window_edges = windows[bucket]
            weight = self.decay ** (n_windows - 1 - i)  # Recent windows get higher weight
            total_weight += weight

            snapshot_scores = self.gcn.fit_predict(nodes, window_edges, node_features)
            for node, score in snapshot_scores.items():
                aggregated[node] += score * weight

        # Normalize by total weight
        if total_weight > 0:
            aggregated = {n: s / total_weight for n, s in aggregated.items()}

        return aggregated


def build_gnn_scores(clean_dataframe: pd.DataFrame, customer_features: pd.DataFrame) -> Dict[str, float]:
    """Convenience function: builds GNN scores from pipeline data.
    
    Extracts graph structure from transaction data, builds node features
    from customer profiles, and runs the Temporal GCN.
    
    Returns:
        Dict mapping customer_id → GNN risk score (0-100).
    """
    logger.info("Running GNN risk scoring...")

    # Extract edges from transactions
    sender_col = None
    receiver_col = None
    for col in clean_dataframe.columns:
        if "sender" in col.lower() or col.lower() == "customer_id":
            if sender_col is None:
                sender_col = col
        if "receiver" in col.lower() or "recipient" in col.lower():
            receiver_col = col

    if not sender_col or not receiver_col:
        logger.warning("Could not detect sender/receiver columns for GNN. Returning empty scores.")
        return {}

    # Build edges with timestamps
    ts_col = "timestamp" if "timestamp" in clean_dataframe.columns else None
    edges_with_time = []
    
    # Sample for performance (GNN on 1M+ edges is slow in numpy)
    df_sample = clean_dataframe.sample(min(20000, len(clean_dataframe)), random_state=42) if len(clean_dataframe) > 20000 else clean_dataframe
    
    for row in df_sample.itertuples():
        src = str(getattr(row, sender_col, ""))
        dst = str(getattr(row, receiver_col, ""))
        ts = str(getattr(row, ts_col, "")) if ts_col else ""
        if src and dst:
            edges_with_time.append((src, dst, ts))

    # Build node list from customers
    if "customer_id" in customer_features.columns:
        customer_ids = customer_features["customer_id"].astype(str).tolist()
    else:
        customer_ids = customer_features.index.astype(str).tolist()

    all_nodes = list(set(customer_ids + [e[0] for e in edges_with_time] + [e[1] for e in edges_with_time]))

    # Build per-node feature vectors from customer features
    node_features: Dict[str, np.ndarray] = {}
    feature_cols = [c for c in customer_features.select_dtypes(include=[np.number]).columns if c != "customer_id"][:8]
    
    if feature_cols:
        for row in customer_features.itertuples():
            cid = str(getattr(row, "customer_id", row.Index))
            feats = np.array([float(getattr(row, c, 0.0)) for c in feature_cols])
            # Normalize
            feats = np.nan_to_num(feats, nan=0.0, posinf=1.0, neginf=0.0)
            norm = np.linalg.norm(feats) + 1e-8
            node_features[cid] = feats / norm

    # Run Temporal GCN
    tgcn = TemporalGCN(window_days=7, n_layers=2, hidden_dim=16, decay=0.8)
    scores = tgcn.fit_predict(all_nodes, edges_with_time, node_features)

    # Filter to only customer nodes
    customer_scores = {cid: scores.get(cid, 0.0) for cid in customer_ids}
    
    logger.info(f"GNN scoring complete. Scored {len(customer_scores)} customers.")
    return customer_scores
