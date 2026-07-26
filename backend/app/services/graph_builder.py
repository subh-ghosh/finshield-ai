"""Service responsible for deterministically constructing the Knowledge Graph."""

import pandas as pd
import hashlib

from app.models.graph_models import GraphNode, GraphEdge
from app.types.graph import NodeType, RelationshipType
from app.services.graph_adapter import IGraphAdapter
from app.utils.logger import get_logger

logger = get_logger(__name__)

class GraphBuilder:
    """Builds the financial graph deterministically from cached dataset structures."""

    def __init__(self, adapter: IGraphAdapter):
        self.adapter = adapter

    def build(self, clean_dataframe: pd.DataFrame, customer_features: pd.DataFrame) -> None:
        """
        Populate the graph adapter using transactions and engineered features.
        
        Args:
            clean_dataframe: Raw transaction logs (validated).
            customer_features: Engineered profile metrics per customer.
        """
        logger.info("Starting deterministic graph build...")
        self.adapter.clear()
        
        self._build_customers(customer_features)
        self._build_transactions_and_accounts(clean_dataframe)
        
        logger.info("Graph build complete.")

    def _synthesize_id(self, base: str, prefix: str) -> str:
        """Synthesize a deterministic linked ID based on a base ID and a prefix."""
        # We drop the last character of the customer ID to create deliberate 
        # but deterministic collisions (shared devices/IPs) for the mock data
        base_collision = base[:-1] if len(base) > 1 else base
        hash_val = hashlib.md5(f"{base_collision}_{prefix}".encode()).hexdigest()[:6]
        return f"{prefix}_{hash_val.upper()}"

    def _build_customers(self, customer_features: pd.DataFrame) -> None:
        if 'customer_id' in customer_features.columns:
            customers = customer_features.to_dict('records')
            id_col = 'customer_id'
        else:
            customer_features = customer_features.reset_index()
            id_col = customer_features.columns[0]
            customers = customer_features.to_dict('records')
            
        for row in customers:
            c_id = str(row[id_col])
            
            # Create Customer Node
            if not self.adapter.has_node(c_id):
                self.adapter.add_node(GraphNode(
                    id=c_id,
                    label=f"Customer {c_id}",
                    type=NodeType.CUSTOMER,
                    metadata={"risk_score": float(row.get("risk_score", 0.0))}
                ))
            
            # Synthesize deterministic devices/IPs to create a realistic network structure
            device_id = self._synthesize_id(c_id, "DEV")
            if not self.adapter.has_node(device_id):
                self.adapter.add_node(GraphNode(
                    id=device_id, label=f"Device {device_id}", type=NodeType.DEVICE
                ))
            self.adapter.add_edge(GraphEdge(
                source=c_id, target=device_id, relationship=RelationshipType.USES_DEVICE
            ))
            
            ip_id = self._synthesize_id(c_id, "IP")
            if not self.adapter.has_node(ip_id):
                self.adapter.add_node(GraphNode(
                    id=ip_id, label=f"IP {ip_id}", type=NodeType.IP
                ))
            self.adapter.add_edge(GraphEdge(
                source=c_id, target=ip_id, relationship=RelationshipType.USES_IP
            ))

    def _build_transactions_and_accounts(self, df: pd.DataFrame) -> None:
        """Process transactions to build accounts and transactional edges."""
        for row in df.itertuples():
            c_id = str(getattr(row, 'customer_id', ''))
            sender_acc = str(getattr(row, 'sender_account', ''))
            receiver_acc = str(getattr(row, 'receiver_account', ''))
            txn_id = str(getattr(row, 'transaction_id', ''))
            amount = float(getattr(row, 'amount', 0.0))
            timestamp = str(getattr(row, 'timestamp', ''))
            currency = str(getattr(row, 'currency', 'USD'))
            
            # Ensure sender account exists
            if not self.adapter.has_node(sender_acc):
                self.adapter.add_node(GraphNode(
                    id=sender_acc, label=f"Acc {sender_acc}", type=NodeType.ACCOUNT
                ))
                
            # Ensure receiver account exists
            if not self.adapter.has_node(receiver_acc):
                self.adapter.add_node(GraphNode(
                    id=receiver_acc, label=f"Acc {receiver_acc}", type=NodeType.ACCOUNT
                ))
                
            # Customer owns sender account (AMLSim data model)
            if c_id and self.adapter.has_node(c_id):
                self.adapter.add_edge(GraphEdge(
                    source=c_id, target=sender_acc, relationship=RelationshipType.OWNS_ACCOUNT
                ))
            
            # Transaction as an edge between accounts
            self.adapter.add_edge(GraphEdge(
                source=sender_acc,
                target=receiver_acc,
                relationship=RelationshipType.TRANSACTS_WITH,
                weight=amount,
                timestamp=timestamp,
                metadata={
                    "transaction_id": txn_id, 
                    "currency": currency,
                    "amount": amount
                }
            ))
