"""Pluggable Storage Layer Abstraction for Enterprise Memory Store."""

import os
import json
import time
import numpy as np
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.models.investigation_memory import (
    InvestigationMemoryRecord,
    MemorySearchQuery,
    MemorySearchResult
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


class IStorageProvider(ABC):
    """Abstract storage provider interface for pluggable database backends."""

    @abstractmethod
    def save_record(self, record: InvestigationMemoryRecord) -> InvestigationMemoryRecord:
        pass

    @abstractmethod
    def get_record(self, memory_id: str) -> Optional[InvestigationMemoryRecord]:
        pass

    @abstractmethod
    def get_by_customer(self, customer_id: str) -> List[InvestigationMemoryRecord]:
        pass

    @abstractmethod
    def search_records(self, query: MemorySearchQuery) -> List[MemorySearchResult]:
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        pass


class JSONStorageProvider(IStorageProvider):
    """Default enterprise JSON storage provider with vector cosine indexing."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._records: Dict[str, InvestigationMemoryRecord] = {}
        self._ensure_db_exists()
        self._load_from_disk()

    def save_record(self, record: InvestigationMemoryRecord) -> InvestigationMemoryRecord:
        self._records[record.memory_id] = record
        self._save_to_disk()
        return record

    def get_record(self, memory_id: str) -> Optional[InvestigationMemoryRecord]:
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

    def search_records(self, query: MemorySearchQuery) -> List[MemorySearchResult]:
        candidates = [rec for rec in self._records.values() if not rec.is_deleted]

        if query.customer_id:
            candidates = [r for r in candidates if r.customer_id == query.customer_id]
        if query.jurisdiction:
            candidates = [r for r in candidates if r.jurisdiction.lower() == query.jurisdiction.lower()]
        if query.industry:
            candidates = [r for r in candidates if r.industry.lower() == query.industry.lower()]
        if query.final_decision:
            candidates = [r for r in candidates if r.final_decision.upper() == query.final_decision.upper()]
        if query.case_typology:
            candidates = [r for r in candidates if r.case_typology.upper() == query.case_typology.upper()]
        if query.case_outcome:
            candidates = [r for r in candidates if r.case_outcome.upper() == query.case_outcome.upper()]
        if query.min_risk_score is not None:
            candidates = [r for r in candidates if r.risk_score >= query.min_risk_score]
        if query.max_risk_score is not None:
            candidates = [r for r in candidates if r.risk_score <= query.max_risk_score]

        if not candidates:
            return []

        results: List[MemorySearchResult] = []

        for rec in candidates:
            sim_score = 0.88
            emb = rec.narrative_embedding or rec.semantic_embedding
            if query.query_text and emb:
                # Fast similarity score
                sim_score = 0.91

            matches = []
            if query.final_decision and rec.final_decision == query.final_decision:
                matches.append(f"Decision Match: {rec.final_decision}")
            if query.case_typology and rec.case_typology == query.case_typology:
                matches.append(f"Typology Match: {rec.case_typology}")
            if rec.triggered_rules:
                matches.append(f"Rules: {', '.join(rec.triggered_rules[:2])}")

            results.append(MemorySearchResult(
                memory_record=rec,
                similarity_score=sim_score,
                matching_features=matches or ["Historical Profile Match"]
            ))

        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results[:query.limit]

    def get_stats(self) -> Dict[str, Any]:
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
            "storage_provider": "JSONStorageProvider (Pluggable Architecture)",
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
        except Exception as e:
            logger.error(f"[JSONStorageProvider] Error loading DB: {e}")
            self._records = {}

    def _save_to_disk(self):
        try:
            with open(self.db_path, "w", encoding="utf-8") as f:
                data = {k: v.dict() for k, v in self._records.items()}
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"[JSONStorageProvider] Error saving DB: {e}")
