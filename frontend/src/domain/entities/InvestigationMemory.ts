export interface MemoryFeatureVector {
  riskScore: number;
  ruleScore: number;
  mlAnomalyScore: number;
  structuringScore: number;
  velocityScore: number;
  cashRatio: number;
  crossBorderRatio: number;
  denseVector: number[];
}

export interface StoreMemoryRequest {
  caseId: string;
  customerId: string;
  customerName?: string;
  customerType?: string;
  industry?: string;
  jurisdiction?: string;
  riskScore: number;
  finalDecision: string;
  disposition?: string;
  triggeredRules?: string[];
  behavioralFeatures?: Record<string, number>;
  isolationForestScore?: number;
  hybridRiskScore?: number;
  networkMetrics?: Record<string, any>;
  evidenceSummary?: string[];
  complianceCompletenessScore?: number;
  missingEvidencePillars?: string[];
  investigationSummary?: string;
  sarNarrative?: string;
  analystNotes?: string;
  investigationDurationSec?: number;
  caseTypology?: string;
}

export interface InvestigationMemoryRecord {
  memoryId: string;
  caseId: string;
  customerId: string;
  customerName: string;
  customerType: string;
  industry: str;
  jurisdiction: string;
  investigationDate: string;
  riskScore: number;
  finalDecision: string;
  disposition: string;
  caseTypology: string;
  triggeredRules: string[];
  behavioralFeatures: Record<string, number>;
  isolationForestScore: number;
  hybridRiskScore: number;
  networkMetrics: Record<string, any>;
  evidenceSummary: string[];
  complianceCompletenessScore: number;
  missingEvidencePillars: string[];
  investigationSummary: string;
  sarNarrative?: string;
  analystNotes?: string;
  investigationDurationSec: number;
  featureVector: MemoryFeatureVector;
  semanticEmbedding: number[];
  version: number;
  timestamp: number;
}

export interface MemorySearchResult {
  memoryRecord: InvestigationMemoryRecord;
  similarityScore: number;
  matchingFeatures: string[];
}

export interface MemoryStatistics {
  totalStoredInvestigations: number;
  decisions: {
    FILE_SAR: number;
    ESCALATE: number;
    MANUAL_REVIEW: number;
    CLEAR: number;
  };
  averageRiskScore: number;
  caseTypologies: Record<string, number>;
  repositoryStatus: string;
  lastUpdated: string;
}
