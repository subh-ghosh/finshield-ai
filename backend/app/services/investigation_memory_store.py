"""Enterprise Investigation Memory Store Service.

Pluggable Storage Layer architecture delegating persistence to IStorageProvider implementations
and integrating the deterministic TypologyClassifier.
"""

import os
import time
import uuid
from typing import List, Dict, Any, Optional
from app.models.investigation_memory import (
    StoreMemoryRequest,
    InvestigationMemoryRecord,
    MemorySearchQuery,
    MemorySearchResult,
    TimelineEvent
)
from app.services.embedding_generator import MemoryEmbeddingGenerator
from app.services.typology_classifier import TypologyClassifier
from app.services.storage_providers import IStorageProvider, JSONStorageProvider
from app.utils.logger import get_logger

logger = get_logger(__name__)

DB_FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "investigation_memory_db.json")


class InvestigationMemoryStore:
    """Enterprise Memory Repository operating over pluggable IStorageProvider implementations."""

    def __init__(self, provider: Optional[IStorageProvider] = None):
        self.provider = provider or JSONStorageProvider(db_path=DB_FILE_PATH)
        self.embedding_generator = MemoryEmbeddingGenerator()
        self.typology_classifier = TypologyClassifier()

    def store(self, req: StoreMemoryRequest) -> InvestigationMemoryRecord:
        """Stores a completed investigation into institutional memory with pluggable persistence."""
        memory_id = f"MEM-{uuid.uuid4().hex[:8].upper()}"
        today_str = time.strftime("%Y-%m-%d")

        # 1. Deterministic Typology Classification (Upgrade 2)
        typology = self.typology_classifier.classify(req).value

        # 2. Chronological Timeline Events Construction (Upgrade 3)
        timeline = req.timeline or [
            TimelineEvent(event_type="ALERT_CREATED", actor="SYSTEM", description="AML Alert Generated", source="RULE_ENGINE"),
            TimelineEvent(event_type="RULE_VALIDATION", actor="RULE_ENGINE", description=f"Rules triggered: {req.triggered_rules}", source="RULE_ENGINE"),
            TimelineEvent(event_type="HYBRID_RISK_EVALUATED", actor="HYBRID_RISK_ENGINE", description=f"Risk score computed as {req.risk_score}", source="HYBRID_RISK_ENGINE"),
            TimelineEvent(event_type="DECISION_GENERATED", actor="DECISION_ENGINE", description=f"Final recommendation: {req.final_decision}", source="DECISION_ENGINE"),
            TimelineEvent(event_type="CASE_CLOSED", actor="ANALYST", description="Case dispositioned & archived into memory", source="INVESTIGATION_WORKSPACE")
        ]

        # 3. Dual Vector Embeddings (Upgrade 5: Narrative Embedding)
        feat_vector = self.embedding_generator.generate_feature_vector(req)
        text_corpus = f"{req.investigation_summary} {' '.join(req.evidence_summary)} {req.sar_narrative or ''} {req.analyst_notes or ''}"
        narrative_emb = self.embedding_generator.generate_semantic_embedding(text_corpus)

        record = InvestigationMemoryRecord(
            memory_id=memory_id,
            case_id=req.case_id,
            customer_id=req.customer_id,
            customer_name=req.customer_name or "Unknown",
            customer_type=req.customer_type,
            industry=req.industry,
            jurisdiction=req.jurisdiction,
            investigation_date=today_str,
            risk_score=req.risk_score,
            final_decision=req.final_decision,
            disposition=req.disposition,
            case_outcome=req.case_outcome or "CLOSED",
            case_typology=typology,
            triggered_rules=req.triggered_rules,
            behavioral_features=req.behavioral_features,
            isolation_forest_score=req.isolation_forest_score,
            hybrid_risk_score=req.hybrid_risk_score,
            network_metrics=req.network_metrics,
            evidence_summary=req.evidence_summary,
            compliance_completeness_score=req.compliance_completeness_score,
            missing_evidence_pillars=req.missing_evidence_pillars,
            investigation_summary=req.investigation_summary,
            sar_narrative=req.sar_narrative,
            analyst_notes=req.analyst_notes,
            investigation_duration_sec=req.investigation_duration_sec,
            timeline=timeline,
            feature_vector=feat_vector,
            narrative_embedding=narrative_emb,
            semantic_embedding=narrative_emb,  # Backward compatibility
            version=1,
            timestamp=time.time(),
            is_deleted=False
        )

        saved = self.provider.save_record(record)
        logger.info(f"[MemoryStore] Stored record {memory_id} via {self.provider.__class__.__name__}.")
        return saved

    def get_by_id(self, memory_id: str) -> Optional[InvestigationMemoryRecord]:
        return self.provider.get_record(memory_id)

    def get_by_customer(self, customer_id: str) -> List[InvestigationMemoryRecord]:
        return self.provider.get_by_customer(customer_id)

    def search(self, query: MemorySearchQuery) -> List[MemorySearchResult]:
        return self.provider.search_records(query)

    def get_statistics(self) -> Dict[str, Any]:
        return self.provider.get_stats()
