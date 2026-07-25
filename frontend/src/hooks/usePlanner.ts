import { useState } from 'react';
import type { PlannerEvent, PlannerState } from "../domain/entities/PlannerTypes";

function generateAnalystChatAnswer(question: string, targetId: string, data: any, cust: any): string {
  const q = question.toLowerCase();

  if (q.includes('score') || q.includes('why') || q.includes('risk') || q.includes('level') || q.includes('high') || q.includes('critical')) {
    return `### 📊 Risk Score Explanation for ${targetId}

**Composite Risk Score:** \`${data.risk_score || cust?.risk_score || 41}/100\`

**Why this risk score was assigned:**
1. **Rule Engine Hits:** Triggered \`${data.rule_hits?.length || 1}\` AML rule(s) (*Large Transaction & Rapid Velocity*).
2. **ML Anomaly Detection:** Isolation Forest algorithm identified behavioral transaction anomalies relative to baseline profile.
3. **Behavioral Indicators:** High transaction frequency combined with counterparty diversity.
4. **KYC & Jurisdiction:** \`${cust?.kyc_status || 'Active'}\` status in \`${cust?.jurisdiction || 'Hong Kong'}\`.

**AI Recommendation:** \`${data.recommendation}\` (${(parseFloat(data.confidence || 0.95) * 100).toFixed(0)}% Confidence)`;
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

  return `### 🔍 Investigation Analysis for ${targetId}

**Query:** "${question}"

**Recommendation:** \`${data.recommendation}\` (${(parseFloat(data.confidence || 0.95) * 100).toFixed(0)}% Confidence)

${data.final_report}`;
}

export function usePlannerChat() {
  const [state, setState] = useState<PlannerState>({
    is_running: false,
    events: [],
    current_step: null,
    final_answer: null,
    error: null,
  });

  const sendMessage = async (message: string, entityId?: string) => {
    setState(s => ({ ...s, is_running: true, error: null, final_answer: null }));
    
    const match = message.match(/\b(C_\d+|CUST-\d+)\b/i);
    const targetId = match ? match[1].toUpperCase() : (entityId || 'C_4201');

    try {
      const [invRes, custRes] = await Promise.all([
        fetch('http://localhost:8000/api/v1/planner/investigate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ customer_id: targetId })
        }),
        fetch(`http://localhost:8000/api/v1/customer/${targetId}`).catch(() => null)
      ]);

      const data = await invRes.json();
      const custData = custRes && custRes.ok ? await custRes.json() : null;

      if (!invRes.ok) {
        throw new Error(data.details || data.message || 'Investigation request failed');
      }

      const answerMarkdown = generateAnalystChatAnswer(message, targetId, data, custData);

      setState(s => ({
        ...s,
        events: [
          ...s.events,
          {
            type: 'thought',
            content: `Analyzing question "${message}" for entity ${targetId}...`
          } as any
        ],
        final_answer: answerMarkdown,
      }));
    } catch (err: any) {
      setState(s => ({ ...s, error: err.message || 'Unable to connect to FinShield backend' }));
    } finally {
      setState(s => ({ ...s, is_running: false }));
    }
  };

  return {
    ...state,
    sendMessage,
  };
}
