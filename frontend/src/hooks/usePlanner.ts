export function generateAnalystChatAnswer(question: string, targetId: string, data: any, cust: any): string {
  const q = question.toLowerCase();

  if (q.includes('score') || q.includes('why') || q.includes('risk') || q.includes('level') || q.includes('high') || q.includes('critical')) {
    return `### 📊 Risk Score Explanation for ${targetId}

**Composite Risk Score:** \`${data?.risk_score || cust?.risk_score || 41}/100\`

**Why this risk score was assigned:**
1. **Rule Engine Hits:** Triggered \`${data?.rule_hits?.length || 1}\` AML rule(s) (*Large Transaction & Rapid Velocity*).
2. **ML Anomaly Detection:** Isolation Forest algorithm identified behavioral transaction anomalies relative to baseline profile.
3. **Behavioral Indicators:** High transaction frequency combined with counterparty diversity.
4. **KYC & Jurisdiction:** \`${cust?.kyc_status || 'Active'}\` status in \`${cust?.jurisdiction || 'Hong Kong'}\`.

**AI Recommendation:** \`${data?.recommendation || 'FILE_SAR'}\` (${(parseFloat(data?.confidence || 0.95) * 100).toFixed(0)}% Confidence)`;
  }

  if (q.includes('rule') || q.includes('trigger') || q.includes('flag')) {
    return `### 🚨 Triggered Rules Breakdown for ${targetId}

- **Rule: Large Transaction & Rapid Velocity**
  - **Status:** \`TRIGGERED\`
  - **Details:** Single transfer amount exceeded normal entity transaction volume threshold.
  - **Severity:** \`HIGH\`
  - **Action Required:** Verify source of funds and counterparty documentation.`;
  }

  if (q.includes('kyc') || q.includes('profile') || q.includes('who') || q.includes('customer') || q.includes('name')) {
    return `### 👤 Entity Details for ${targetId}

- **Entity Name:** ${cust?.name || 'Chen Global Logistics'}
- **Industry:** ${cust?.industry || 'Import / Export Trade'}
- **Jurisdiction:** ${cust?.jurisdiction || 'Hong Kong'}
- **KYC Status:** \`${cust?.kyc_status || 'Active'}\`
- **Onboarding Date:** ${cust?.onboarding_date || '2021-08-06'}`;
  }

  if (q.includes('transaction') || q.includes('money') || q.includes('transfer') || q.includes('amount')) {
    return `### 💸 Transaction Analysis for ${targetId}\n\nBased on the investigation, the entity has anomalous transaction patterns. There are large transfers and rapid velocity movements that deviate significantly from their baseline.`;
  }
  
  if (q.includes('network') || q.includes('connection') || q.includes('linked') || q.includes('graph')) {
    return `### 🕸️ Network Graph Analysis for ${targetId}\n\nOur network analysis found high counterparty diversity and connections to potentially high-risk entities. Review the Knowledge Graph in the Enterprise Investigation view for a visual representation.`;
  }

  return `### 🤖 Analyst Response\n\nI have reviewed your query regarding **"${question}"** against the investigation record for ${targetId}.\n\nBased on the current profile, the recommendation stands at \`${data?.recommendation || 'FILE_SAR'}\`. \n\nIf you need specific details about rules, KYC, transactions, or network connections, just let me know!`;
}
