import type { EvidenceGapAssessmentDTO, ComplianceItemEvaluationDTO } from '../dtos/EvidenceGapDTO';
import type { EvidenceGapAssessment, ComplianceItemEvaluation, CompliancePillar, EvidenceItemStatus } from '../../domain/entities/EvidenceGap';

export class EvidenceGapMapper {
  static toDomain(dto: EvidenceGapAssessmentDTO): EvidenceGapAssessment {
    return {
      customerId: dto.customer_id,
      completenessScore: dto.completeness_score,
      sarFilingReady: dto.sar_filing_ready,
      blockingCriticalGapsCount: dto.blocking_critical_gaps_count,
      totalItemsEvaluated: dto.total_items_evaluated,
      passedItemsCount: dto.passed_items_count,
      evaluations: dto.evaluations.map(this.mapEvaluationToDomain),
      warnings: dto.warnings || [],
      missingCriticalItems: dto.missing_critical_items || [],
      missingOptionalItems: dto.missing_optional_items || [],
      remediationRoadmap: dto.remediation_roadmap || [],
    };
  }

  private static mapEvaluationToDomain(dto: ComplianceItemEvaluationDTO): ComplianceItemEvaluation {
    return {
      pillar: dto.pillar as CompliancePillar,
      name: dto.name,
      status: dto.status as EvidenceItemStatus,
      weight: dto.weight,
      isRequiredForSar: dto.is_required_for_sar,
      description: dto.description,
      remediationAction: dto.remediation_action,
    };
  }
}
