"""Consolidated pipeline result schema definition with detailed metadata fields."""

from dataclasses import dataclass, field
from typing import Any, Dict, List
import pandas as pd
from app.models.analysis_result import AnalysisResult
from app.services.preprocessing import PreprocessingReport

@dataclass
class PipelineResult:
    """Structure encapsulating all outputs and metadata metrics of the completed pipeline run."""
    clean_dataframe: pd.DataFrame
    customer_features: pd.DataFrame
    rule_analysis: List[AnalysisResult]
    rule_dataframe: pd.DataFrame
    anomaly_analysis: List[AnalysisResult]
    anomaly_dataframe: pd.DataFrame
    report: PreprocessingReport
    execution_time: float = 0.0
    pipeline_version: str = "1.0.0"
    model_versions: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
