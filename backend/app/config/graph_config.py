"""Knowledge Graph Intelligence Module Configuration."""

from pydantic_settings import BaseSettings

class GraphConfig(BaseSettings):
    """Type-safe configuration for the Knowledge Graph subsystem."""
    
    # Graph traversal and retrieval limits
    GRAPH_MAX_HOPS: int = 2
    GRAPH_NODE_LIMIT: int = 150
    
    # Cache settings
    GRAPH_CACHE_TTL_SECONDS: int = 3600  # 1 hour
    
    # Analytics thresholds
    GRAPH_COMMUNITY_THRESHOLD: int = 3
    GRAPH_HIGH_RISK_THRESHOLD: float = 75.0
    
    # Default UI layout
    GRAPH_DEFAULT_LAYOUT: str = "force-directed"
    
    model_config = {"env_prefix": "FINSHIELD_"}

# Global singleton configuration for the graph subsystem
graph_config = GraphConfig()
