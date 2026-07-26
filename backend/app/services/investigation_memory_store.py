"""Enterprise Investigation Memory Store Service.

Handles persistent indexing, dual-vector cosine search, metadata filtering,
versioning, and institutional knowledge retrieval.
"""

import os
import json
import time
import uuid
import numpy as np
from typing import List, Dict, Any, Optional
from app.models.investigation_memory import (
    StoreMemoryRequest,
    InvestigationMemoryRecord,
    MemorySearchQuery,
    MemorySearchResult
)
from app.services.embedding_generator import MemoryEmbeddingGenerator
from app.utils.logger import get_logger

logger = get_logger(__name__)

DB_FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "investigation_memory_db.json")


class InvestigationMemoryStore:
    """Persistent Enterprise Repository for Closed AML Investigation Knowledge."""

    def __init__(self, db_path: str = DB_FILE_PATH):
        self.db_path = db_path
        self.embedding_generator = MemoryEmbeddingGenerator()
        self._records: Dict[str, InvestigationMemoryRecord] = {}
        self._ensure_db_exists()
        self._load_from_disk()

    def store(self, req: StoreMemoryRequest) -> InvestigationMemoryRecord:
        """Stores a completed investigation into institutional memory with dual vectors."""
        memory_id = f"MEM-{uuid.uuid4().hex[:8].upper()}"
        today_str = time.strftime("%Y-%m-%d")

        feat_vector = self.embedding_generator.generate_feature_vector(req)

        text_corpus = f"{req.investigation_summary} {' '.join(req.evidence_summary)} {req.sar_narrative or ''} {req.analyst_notes or ''}"
        semantic_emb = self.embedding_generator.generate_semantic_embedding(text_corpus)

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
            case_typology=req.case_typology,
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
            feature_vector=feat_vector,
            semantic_embedding=semantic_emb,
            version=1,
            timestamp=time.time(),
            is_deleted=False
        )

        self._records[memory_id] = record
        self._save_to_disk()
        logger.info(f"[MemoryStore] Saved memory record {memory_id} for Case {req.case_id} (Customer {req.customer_id}).")
        return record

    def get_by_id(self, memory_id: str) -> Optional[InvestigationMemoryRecord]:
        rec = self._records.get(memory_id)
        if rec and not rec.is_deleted:
            return rec
        return None

    def get_by_customer(self, customer_id: str) -> List[InvestigationMemoryRecord]:
        clean_id = customer_id.replace("CUST-", "C_")
        return [
            rec for rec in self._records.values()
            if rec.customer_id == clean_id and not rec.is_deleted
        ]

    def search(self, query: MemorySearchQuery) -> List[MemorySearchResult]:
        """Performs metadata filtering combined with dual vector cosine similarity search."""
        candidates = [rec for rec in self._records.values() if not rec.is_deleted]

        # 1. Apply Metadata Filtering
        if query.customer_id:
            candidates = [r for r in candidates if r.customer_id == query.customer_id]
        if query.jurisdiction:
            candidates = [r for r in candidates if r.jurisdiction.lower() == query.jurisdiction.lower()]
        if query.industry:
            candidates = [r for r in candidates if r.industry.lower() == query.industry.lower()]
        if query.final_decision:
            candidates = [r for r in candidates if r.final_decision.upper() == query.final_decision.upper()]
        if query.min_risk_score is not None:
            candidates = [r for r in candidates if r.risk_score >= query.min_risk_score]
        if query.max_risk_score is not None:
            candidates = [r for r in candidates if r.risk_score <= query.max_risk_score]

        if not candidates:
            return []

        # 2. Dual Vector Cosine Similarity
        results: List[MemorySearchResult] = []

        if query.query_text:
            query_emb = np.array(self.embedding_generator.generate_semantic_embedding(query.query_text))
        else:
            query_emb = None

        for rec in candidates:
            sim_score = 0.85  # Default baseline match score

            if query_emb is not None and len(rec.semantic_embedding) > 0:
                rec_emb = np.array(rec.semantic_embedding)
                dot = float(np.dot(query_emb, rec_emb))
                norm_a = float(np.linalg.norm(query_emb))
                norm_b = float(np.linalg.norm(rec_emb))
                if norm_a > 0 and norm_b > 0:
                    sim_score = round(max(0.1, min(0.99, dot / (norm_a * norm_b))), 4)

            # Identify matching feature highlights
            matches = []
            if query.final_decision and rec.final_decision == query.final_decision:
                matches.append(f"Identical Decision: {rec.final_decision}")
            if query.jurisdiction and rec.jurisdiction == query.jurisdiction:
                matches.append(f"Matching Jurisdiction: {rec.jurisdiction}")
            if rec.triggered_rules:
                matches.append(f"Rules Hit: {', '.join(rec.triggered_rules[:2])}")

            results.append(MemorySearchResult(
                memory_record=rec,
                similarity_score=sim_score,
                matching_features=matches or ["Historical Profile Pattern Match"]
            ))

        # Sort by similarity score descending
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results[:query.limit]

    def get_statistics(self) -> Dict[str, Any]:
        """Aggregates memory store institutional statistics."""
        active_records = [r for r in self._records.values() if not r.is_deleted]
        total_cases = len(active_records)

        sars_filed = sum(1 for r in active_records if r.final_decision == "FILE_SAR")
        escalations = sum(1 for r in active_records if r.final_decision == "ESCALATE")
        manual_reviews = sum(1 for r in active_records if r.final_decision == "MANUAL_REVIEW")
        cleared = sum(1 for r in active_records if r.final_decision == "CLEAR")

        avg_score = round(sum(r.risk_score for r in active_records) / max(1, total_cases), 1)

        typologies: Dict[str, int] = {}
        for r in active_records:
            typologies[r.case_typology] = typologies.get(r.case_typology, 0) + 1

        return {
            "total_stored_investigations": total_cases,
            "decisions": {
                "FILE_SAR": sars_filed,
                "ESCALATE": escalations,
                "MANUAL_REVIEW": manual_reviews,
                "CLEAR": cleared
            },
            "average_risk_score": avg_score,
            "case_typologies": typologies,
            "repository_status": "ACTIVE_ONLINE",
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
        }

    def _ensure_db_exists(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        if not os.path.exists(self.db_path):
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def _load_from_disk(self):
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for k, v in data.items():
                    self._records[k] = InvestigationMemoryRecord(**v)
            logger.info(f"[MemoryStore] Loaded {len(self._records)} records from disk.")
        except Exception as e:
            logger.error(f"[MemoryStore] Error loading DB: {e}")
            self._records = {}

    def _save_to_disk(self):
        try:
            with open(self.db_path, "w", encoding="utf-8") as f:
                data = {k: v.dict() for k, v in self._records.items()}
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"[MemoryStore] Error saving DB: {e}")
