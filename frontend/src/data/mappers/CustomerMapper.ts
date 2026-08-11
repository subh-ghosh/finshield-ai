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
    // Map severity to standard enum with safe fallbacks
    const ruleSev = dto.rule_summary?.severity || 'LOW';
    const anomSev = dto.anomaly_summary?.severity || 'LOW';
    let riskLevel: 'Critical' | 'High' | 'Medium' | 'Low' = 'Low';
    if (ruleSev === 'CRITICAL' || anomSev === 'CRITICAL') riskLevel = 'Critical';
    else if (ruleSev === 'HIGH' || anomSev === 'HIGH') riskLevel = 'High';
    else if (ruleSev === 'MEDIUM' || anomSev === 'MEDIUM') riskLevel = 'Medium';

    const ruleScore = dto.rule_summary?.score ?? 20;
    const anomScore = dto.anomaly_summary?.anomaly_score ?? 0.45;
    const rawScore = ruleScore + Math.round(anomScore * 50);
    const riskScore = Math.min(Math.max(rawScore, 10), 99);
    const id = dto.customer_id;
    const hash = getHash(id);

    // Known customer names for demo
    const knownNames: Record<string, string> = {
      "C_9358": "Julia Patel",
      "C_3762": "Gallagher Trading Ltd",
      "C_1204": "Astra Maritime Logistics",
      "C_5519": "Vanguard Tech Holdings",
      "C_8410": "Apex Minerals Corp",
      "C_2190": "Crestview Holdings",
      "C_4301": "Horizon Energy Group",
      "C_6122": "Solaria Retail Ventures",
      "C_1088": "BlueSky Media Inc"
    };

    return {
      id: dto.customer_id,
      name: knownNames[id] || generateEntityName(id),
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
      recent_transactions: (() => {
        const txTypes = ['Wire Transfer', 'SWIFT Transfer', 'SEPA Transfer', 'ACH Credit', 'Domestic Transfer'];
        const statuses = ['completed', 'completed', 'completed', 'pending', 'flagged'];
        const parties = [
          `${generateEntityName(`party_${id}_1`)} Inc`,
          `${generateEntityName(`party_${id}_2`)} Ltd`,
          `${generateEntityName(`party_${id}_3`)} Corp`,
          `${generateEntityName(`party_${id}_4`)} Group`,
          `${generateEntityName(`party_${id}_5`)} Holdings`,
        ];
        const baseAmt = dto.feature_metrics?.average_amount || 25000;
        return Array.from({ length: 5 }, (_, i) => {
          const d = new Date();
          d.setDate(d.getDate() - (i * 7));
          const amt = Math.round(baseAmt * (0.5 + ((hash * (i + 1)) % 150) / 100));
          return {
            date: d.toISOString().split('T')[0],
            amount: `$${amt.toLocaleString()}`,
            type: txTypes[(hash + i) % txTypes.length],
            status: statuses[(hash + i) % statuses.length],
            party: parties[i % parties.length],
          };
        });
      })()
    };
  }
}

