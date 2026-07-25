"""Lightweight model training metadata schema definition."""

from dataclasses import dataclass
from typing import List

@dataclass
class ModelMetadata:
    """Stores lightweight metrics tracking model name, feature set, and train timestamp."""
    model_name: str
    version: str
    trained_at: float
    feature_names: List[str]
    random_state: int
