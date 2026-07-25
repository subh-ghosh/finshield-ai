"""Aggregated context representing intermediate and final outputs of an AML run."""

from dataclasses import dataclass, field
from typing import Any, Dict, List
import pandas as pd
from app.models.analysis_result import AnalysisResult

@dataclass
class PipelineContext:
    """Carries full state across preprocessing, rule evaluation, and model prediction stages."""
    customer_features: pd.DataFrame
    rule_results: List[AnalysisResult]
    ml_results: List[AnalysisResult]
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    pipeline_version: str = "1.0.0"
    dataset_info: Dict[str, Any] = field(default_factory=dict)
