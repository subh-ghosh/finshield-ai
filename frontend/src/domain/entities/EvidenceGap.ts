export type CompliancePillar =
  | 'KYC_VERIFICATION'
  | 'SOURCE_OF_FUNDS'
  | 'BENEFICIAL_OWNERSHIP'
  | 'TRANSACTION_EVIDENCE'
  | 'NETWORK_ANALYSIS'
  | 'RULE_VALIDATION'
  | 'EXTERNAL_VERIFICATION'
  | 'ANALYST_NOTES';

export type EvidenceItemStatus =
  | 'PRESENT'
  | 'MISSING_CRITICAL'
  | 'MISSING_OPTIONAL'
  | 'WARNING';

export interface ComplianceItemEvaluation {
  pillar: CompliancePillar;
  name: string;
  status: EvidenceItemStatus;
  weight: number;
  isRequiredForSar: boolean;
  description: string;
  remediationAction: string;
}

export interface EvidenceGapAssessment {
  customerId: string;
  completenessScore: number;
  sarFilingReady: boolean;
  blockingCriticalGapsCount: number;
  totalItemsEvaluated: number;
  passedItemsCount: number;
  evaluations: ComplianceItemEvaluation[];
  warnings: string[];
  missingCriticalItems: string[];
  missingOptionalItems: string[];
  remediationRoadmap: string[];
}
