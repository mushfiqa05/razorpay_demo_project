import React, { useState } from 'react';
import { HelpCircle, Info, Check, ShieldCheck } from 'lucide-react';

export default function PriorityExplanationCard() {
  const [expanded, setExpanded] = useState(false);

  return (
    <div style={{ background: 'var(--razorpay-light-blue)', border: '1px solid #BFDBFE', borderRadius: '8px', padding: '14px 16px', fontSize: '0.82rem', color: 'var(--razorpay-navy)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 600 }}>
          <Info size={16} color="var(--razorpay-blue)" />
          <span>Priority Sweet Spot Architecture</span>
        </div>
        <button 
          onClick={() => setExpanded(!expanded)} 
          style={{ background: 'transparent', border: 'none', color: 'var(--razorpay-blue)', fontSize: '0.78rem', padding: 0, fontWeight: 600 }}
        >
          {expanded ? 'Hide Calculation' : 'How Priority Works?'}
        </button>
      </div>

      <p style={{ marginTop: '6px', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
        High-value opportunities with high recoverability are prioritized first. We rank by <strong>Expected Recoverable Value</strong> rather than raw transaction size.
      </p>

      {expanded && (
        <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid #DBEAFE', display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '0.78rem', color: 'var(--text-primary)' }}>
          <div style={{ fontWeight: 600, color: 'var(--razorpay-navy)', marginBottom: '2px' }}>
            Priority Score Formula Weighting:
          </div>
          <div>• <strong>50% Expected Recoverable Value</strong> (Amount × Recoverability)</div>
          <div>• <strong>20% Recoverability Probability</strong> (Customer past payment history & attempt count)</div>
          <div>• <strong>20% Urgency Score</strong> (Event age & overdue invoice days)</div>
          <div>• <strong>10% Customer Loyalty Tier</strong> (High-value vs Standard customer profile)</div>
        </div>
      )}
    </div>
  );
}
