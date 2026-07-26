import type { InvestigationMemoryRecord } from './InvestigationMemory';

export interface SimilarityBreakdown {
  featureVectorSimilarity: number;
  narrativeSimilarity: number;
  ruleOverlapScore: number;
  typologyMatchScore: number;
  customerProfileSimilarity: number;
  jurisdictionSimilarity: number;
  timelineSimilarity: number;
  overallSimilarityScore: number;
}

export interface SimilarCaseResult {
  caseId: string;
  customerId: string;
  customerName: string;
  riskScore: number;
  finalDecision: string;
  caseOutcome: string;
  caseTypology: string;
  investigationDate: string;
  investigationDurationSec: number;
  estimatedAnalystTimeSavedMin: number;
  primaryRules: string[];
  similarityBreakdown: SimilarityBreakdown;
  deterministicReasons: string[];
  memoryRecord: InvestigationMemoryRecord;
}

export interface SimilarCasesResponse {
  currentInvestigationId: string;
  totalMatchesFound: number;
  executiveSimilaritySummary: string;
  averageSimilarityPct: number;
  similarCases: SimilarCaseResult[];
}

export interface CaseComparisonResult {
  currentInvestigationId: string;
  historicalCaseId: string;
  overallSimilarityPct: number;
  executiveComparisonSummary: string;
  riskScoreComparison: { current: number; historical: number };
  decisionComparison: { current: string; historical: string };
  typologyComparison: { current: string; historical: string };
  rulesComparison: { current: string[]; historical: string[] };
  matchingIndicators: string[];
  differenceHighlights: string[];
}
