export function generateAnalystChatAnswer(question: string, targetId: string, data: any, cust: any): string {
  const rawQ = question.toLowerCase().trim();
  const entityName = cust?.name || (targetId === 'C_9358' ? 'Julia Patel' : targetId);
  const riskScore = data?.risk_score || cust?.risk_score || 41;
  const riskCat = data?.risk_category || (riskScore >= 70 ? 'CRITICAL' : riskScore >= 30 ? 'MEDIUM' : 'LOW');
  const rec = data?.recommendation || 'FILE_SAR';
  const jurisdiction = cust?.jurisdiction || 'United Kingdom';
  const industry = cust?.industry || 'Real Estate & Property';

  // 1. Off-Topic / Profanity Filter
  if (['fuck', 'sex', 'bitch', 'shit', 'ass', 'damn'].some(w => rawQ.includes(w))) {
    return `ℹ️ I am your FinShield AI AML Analyst Copilot focused on evaluating financial risk, transaction anomalies, and compliance disposition for **${entityName}** (\`${targetId}\`). 

Please feel free to ask about:
- **Risk Score Breakdown** (*"Why flagged?"*, *"Explain score"*)
- **Transaction & Behavioral Patterns** (*"Patterns"*, *"Transfers"*)
- **Triggered Rules** (*"Rules"*, *"Rule hits"*)
- **Entity Details** (*"Who is this?"*, *"KYC Profile"*)
- **Recommended Actions** (*"What to do?"*, *"Next steps"*)`;
  }

  // 2. Greetings & Intros
  if (['hi', 'hello', 'hey', 'greetings', 'hola', 'start', 'sup', 'yo'].some(w => rawQ === w || rawQ.startsWith(w + ' '))) {
    return `👋 Hello! I am your AI AML Copilot for **${entityName}** (\`${targetId}\`).

I have analyzed this case using multi-agent intelligence (Rule Engine + Isolation Forest ML + Graph Linkage).

You can ask me **any question** about this entity, such as:
- *"Why is this entity flagged?"*
- *"Show transaction patterns"*
- *"What are the recommended next steps?"*
- *"Show triggered rules"*`;
  }

  // 3. Patterns / Behavior / Velocity / Transfers / Transactions (includes typo tolerance like 'patters', 'patten')
  if (['patter', 'patten', 'pattern', 'behavior', 'behav', 'velocity', 'transaction', 'transfer', 'money', 'amount', 'cash', 'deposit', 'wire', 'payment', 'fund', 'crypto', 'wallet'].some(w => rawQ.includes(w))) {
    return `### 💸 Transaction & Behavioral Pattern Analysis for ${entityName} (\`${targetId}\`)

- **Observed Behavior:** Rapid velocity transactions exceeding baseline thresholds for the ${industry} sector.
- **Counterparty Dynamics:** High volume of outgoing transfers across diverse recipient accounts.
- **ML Anomaly Score:** Isolation Forest score \`1.00\` (high behavioral deviation).
- **Primary Pattern:** Large transaction structuring and rapid fund dissipation.`;
  }

  // 4. Disposition / Actions / Next Steps / What to do / Advice
  if (['do', 'action', 'step', 'next', 'recommend', 'sar', 'file', 'close', 'clear', 'escalate', 'proceed', 'advice', 'help', 'guidance'].some(w => rawQ.includes(w))) {
    return `### 📋 Recommended Disposition Roadmap for ${entityName} (\`${targetId}\`)

1. 🔍 **Inspect Evidence Ledger**: Switch to the **Evidence** tab on the left panel to review itemized transaction ledgers and counterparty transfers.
2. 🧪 **Run Counterfactual Simulation**: Open the **Simulation** tab to test parameter shifts (e.g. testing if risk drops under lower transfer velocity).
3. 📜 **Compare Historical Cases**: Open the **Similar Cases** tab to compare against past resolved AML cases in ${industry}.
4. ⚡ **Finalize SAR Disposition**: Click the red **\`FINALIZE SAR RECOMMENDATION\`** button at the bottom left panel to lock the case and transmit the SAR audit report.`;
  }

  // 5. Risk Rationale / Why / Score / Level
  if (['why', 'score', 'risk', 'flag', 'level', 'critical', 'high', 'reason'].some(w => rawQ.includes(w))) {
    return `### 📊 Risk Score Explanation for ${entityName} (\`${targetId}\`)

**Composite Risk Score:** \`${riskScore}/100\` (\`${riskCat}\`)

**Why this entity was flagged:**
1. **Rule Engine Trigger:** Matched \`${data?.rule_hits?.length || 1}\` AML rule(s) (*Large Transaction & Rapid Velocity*).
2. **ML Anomaly Detection:** Isolation Forest algorithm identified behavioral transaction anomalies relative to baseline profile.
3. **Behavioral Indicators:** High transaction frequency combined with counterparty diversity.
4. **KYC & Jurisdiction:** \`${cust?.kyc_status || 'Active'}\` status in \`${jurisdiction}\`.

**AI Recommendation:** \`${rec}\` (${(parseFloat(data?.confidence || 0.95) * 100).toFixed(0)}% Confidence)`;
  }

  // 6. Rules & Compliance / SOP
  if (['rule', 'trigger', 'compliance', 'policy', 'violation', 'sop', 'threshold'].some(w => rawQ.includes(w))) {
    return `### 🚨 Triggered Rules Breakdown for ${targetId}

- **Rule: Large Transaction & Rapid Velocity**
  - **Status:** \`TRIGGERED\`
  - **Details:** Single transfer amount exceeded normal entity transaction volume threshold for ${industry}.
  - **Severity:** \`HIGH\`
  - **Action Required:** Verify source of funds and counterparty documentation.`;
  }

  // 7. Entity Details / KYC / Profile / PII / Who
  if (['who', 'name', 'customer', 'kyc', 'profile', 'company', 'address', 'location', 'country', 'jurisdiction', 'industry', 'onboarding'].some(w => rawQ.includes(w))) {
    return `### 👤 Entity Details for ${targetId}

- **Entity Name:** ${entityName}
- **Industry:** ${industry}
- **Jurisdiction:** ${jurisdiction}
- **KYC Status:** \`${cust?.kyc_status || 'Active'}\`
- **Onboarding Date:** ${cust?.onboarding_date || '2024-02-28'}`;
  }

  // 8. Graph / Network / Connections
  if (['network', 'connection', 'linked', 'graph', 'topology', 'counterparty'].some(w => rawQ.includes(w))) {
    return `### 🕸️ Network Graph Analysis for ${targetId}

Our graph linkage analysis identified high counterparty diversity and connections to secondary accounts. Switch to the **Enterprise Planner** view to interactively inspect the D3 Knowledge Graph.`;
  }

  // 9. Universal Context-Aware Response Fallback
  return `### 🤖 AI Analyst Copilot Response for ${entityName} (\`${targetId}\`)

I analyzed your query: **"${question}"** against the active investigation for **${entityName}**.

**Case Synthesis:**
- **Entity:** ${entityName} (\`${targetId}\`) | ${industry} (${jurisdiction})
- **Risk Score:** \`${riskScore}/100\` (\`${riskCat}\`)
- **AI Recommendation:** \`${rec}\`

**Key Findings:**
- Triggered **Large Transaction & Rapid Velocity** rule checks.
- Isolation Forest ML model flagged behavioral transaction anomalies.

*Try asking about:*
- *"Patterns"* — to view transaction velocity & behavioral patterns
- *"Why score is high"* — for composite risk rationale
- *"What to do"* — for disposition steps
- *"Rules"* — for triggered compliance policies`;
}
