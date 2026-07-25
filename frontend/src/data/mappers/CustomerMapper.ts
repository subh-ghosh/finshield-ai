import type { CustomerProfileDTO } from '../dtos/CustomerProfileDTO';
import type { CustomerProfile } from '../../domain/entities/CustomerProfile';

function getHash(id: string): number {
  let hash = 0;
  for (let i = 0; i < id.length; i++) {
    hash = (hash << 5) - hash + id.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash);
}

function generateEntityName(id: string): string {
  const hash = getHash(id);
  const firstNames = ['Alexander', 'Beatrix', 'Charles', 'Diana', 'Edward', 'Fiona', 'George', 'Hannah', 'Ian', 'Julia', 'Kevin', 'Laura', 'Marcus', 'Nora', 'Oliver', 'Penelope', 'Quentin', 'Rachel', 'Samuel', 'Theresa', 'Victor', 'Wendy', 'Xavier', 'Yasmine', 'Zachary'];
  const lastNames = ['Vance', 'Sterling', 'Chen', 'Patel', 'Kowalski', 'Montgomery', 'Mercer', 'DuPont', 'Rothschild', 'Sinclair', 'Blackwood', 'Holloway', 'Gallagher', 'Hawthorne', 'Kensington', 'Thornton', 'Sutherland', 'Abernathy', 'Winslow', 'Fontaine'];
  const companyTypes = ['Capital Group', 'Holdings Corp', 'Global Logistics', 'International Trust', 'Trading Ltd', 'Ventures Inc', 'Financial Services'];
  
  if (hash % 3 === 0) {
    const ln = lastNames[hash % lastNames.length];
    const comp = companyTypes[(hash * 3) % companyTypes.length];
    return `${ln} ${comp}`;
  } else {
    const fn = firstNames[hash % firstNames.length];
    const ln = lastNames[(hash * 7) % lastNames.length];
    return `${fn} ${ln}`;
  }
}

function generateIndustry(id: string): string {
  const industries = [
    'Banking & Financial Services',
    'Real Estate & Property',
    'Crypto & Digital Assets',
    'Import / Export Trade',
    'Technology & Software',
    'Pharmaceuticals & Health',
    'Luxury Goods & Jewelry',
    'Consulting & Legal'
  ];
  return industries[getHash(id) % industries.length];
}

function generateJurisdiction(id: string): string {
  const jurisdictions = [
    'United States',
    'United Kingdom',
    'Switzerland',
    'Singapore',
    'Cayman Islands',
    'Luxembourg',
    'Hong Kong',
    'United Arab Emirates'
  ];
  return jurisdictions[getHash(id) % jurisdictions.length];
}

function generateOnboardingDate(id: string): string {
  const hash = getHash(id);
  const year = 2020 + (hash % 5);
  const month = String(1 + (hash % 12)).padStart(2, '0');
  const day = String(1 + ((hash * 3) % 28)).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

export class CustomerMapper {
  static toDomain(dto: CustomerProfileDTO): CustomerProfile {
    // Map severity to standard enum
    let riskLevel: 'Critical' | 'High' | 'Medium' | 'Low' = 'Low';
    if (dto.rule_summary.severity === 'CRITICAL' || dto.anomaly_summary.severity === 'CRITICAL') riskLevel = 'Critical';
    else if (dto.rule_summary.severity === 'HIGH' || dto.anomaly_summary.severity === 'HIGH') riskLevel = 'High';
    else if (dto.rule_summary.severity === 'MEDIUM' || dto.anomaly_summary.severity === 'MEDIUM') riskLevel = 'Medium';

    const rawScore = dto.rule_summary.score + Math.round(dto.anomaly_summary.anomaly_score * 50);
    const riskScore = Math.min(Math.max(rawScore, 10), 99);
    const id = dto.customer_id;
    const hash = getHash(id);

    return {
      id: dto.customer_id,
      name: generateEntityName(id),
      kyc_status: hash % 5 === 0 ? 'Under Review' : 'Active',
      risk_score: riskScore,
      onboarding_date: generateOnboardingDate(id),
      industry: generateIndustry(id),
      jurisdiction: generateJurisdiction(id),
      historical_risk: riskLevel,
      connections: [
        {
          id: `C_${(hash % 9000) + 1000}`,
          name: generateEntityName(`conn_${id}_1`),
          role: hash % 2 === 0 ? 'Director' : 'Beneficial Owner',
          risk: hash % 4 === 0 ? 'High' : 'Low'
        },
        {
          id: `C_${((hash * 3) % 9000) + 1000}`,
          name: generateEntityName(`conn_${id}_2`),
          role: 'Counterparty',
          risk: 'Medium'
        }
      ],
      recent_transactions: [
        {
          date: new Date().toISOString().split('T')[0],
          amount: `$${(dto.feature_metrics?.maximum_amount || 25000).toLocaleString()}`,
          type: hash % 2 === 0 ? 'Wire Transfer' : 'SWIFT Transfer',
          status: 'completed',
          party: `${generateEntityName(`party_${id}`)} Inc`
        }
      ]
    };
  }
}

