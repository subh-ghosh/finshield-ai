import type { InvestigationResultDTO } from '../dtos/InvestigationResultDTO';
import type { InvestigationResult } from '../../domain/entities/InvestigationResult';

export class InvestigationMapper {
  static toDomain(dto: InvestigationResultDTO): InvestigationResult {
    let recommendation: 'CLEAR' | 'MANUAL_REVIEW' | 'ESCALATE' | 'FILE_SAR' = 'MANUAL_REVIEW';
    if (['CLEAR', 'MANUAL_REVIEW', 'ESCALATE', 'FILE_SAR'].includes(dto.recommendation)) {
      recommendation = dto.recommendation as any;
    }

    return {
      customerId: dto.customer_id,
      correlationId: dto.correlation_id,
      recommendation,
      confidence: parseFloat(dto.confidence) || 0.0,
      finalReport: dto.final_report,
      toolCalls: dto.tool_calls ? dto.tool_calls.length : 0,
      apiCalls: dto.api_calls,
      executionTimeMs: dto.execution_time_ms,
      reasoningSteps: (dto.reasoning_steps || []).map((step, index) => ({
        step: `Step ${index + 1}`,
        description: step,
        timestamp: new Date().toISOString(),
      })),

      // DTO compatibility properties for UI views
      customer_id: dto.customer_id,
      correlation_id: dto.correlation_id,
      planner_status: dto.planner_status || 'COMPLETED',
      investigation_complete: dto.investigation_complete ?? true,
      final_report: dto.final_report,
      tool_calls: dto.tool_calls || [],
      api_calls: dto.api_calls,
      execution_time_ms: dto.execution_time_ms,
      reasoning_steps: dto.reasoning_steps || [],
      errors: dto.errors || [],
    };
  }
}

