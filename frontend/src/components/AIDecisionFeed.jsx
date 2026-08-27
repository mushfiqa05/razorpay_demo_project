import React from 'react';
import { Bot, ShieldCheck, ShieldAlert } from 'lucide-react';

export default function AIDecisionFeed({ opportunities, onSelectOpportunity }) {
  const oppList = (opportunities || []).slice(0, 5);

  const formatCurrency = (val) => `₹${Number(val || 0).toLocaleString('en-IN')}`;

  const formatType = (type) => {
    switch (type) {
      case 'PAYMENT_FAILURE': return 'Payment Failure';
      case 'CHECKOUT_ABANDONMENT': return 'Checkout Abandonment';
      case 'SUBSCRIPTION_FAILURE': return 'Subscription Failure';
      case 'OVERDUE_INVOICE': return 'Overdue Invoice';
      default: return type || 'Revenue Event';
    }
  };

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', paddingBottom: '12px', borderBottom: '1px solid var(--border-color)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Bot size={18} color="var(--razorpay-blue)" />
          <div>
            <h3 className="title-medium" style={{ fontSize: '1rem' }}>AI Recovery Decision Feed</h3>
            <p className="text-muted" style={{ fontSize: '0.78rem' }}>
              Real-time recommendations & backend guardrail states
            </p>
          </div>
        </div>
        <span className="badge badge-neutral" style={{ fontSize: '0.7rem' }}>LIVE ADVISORY</span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', flex: 1 }}>
        {oppList.length === 0 ? (
          <p className="text-muted" style={{ fontSize: '0.85rem', padding: '24px 0', textAlign: 'center' }}>
            No recent AI recovery decisions recorded.
          </p>
        ) : (
          oppList.map((opp) => {
            // Phase 6.2 Fix #7: Guardrail status comes strictly from backend event status
            const isBlocked = opp.status === 'STOPPED' || opp.status === 'FAILED';
            return (
              <div 
                key={opp.event_id}
                onClick={() => onSelectOpportunity(opp.event_id)}
                style={{
                  padding: '12px',
                  background: 'var(--bg-subtle)',
                  borderRadius: '8px',
                  border: '1px solid var(--border-color)',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                  <span style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                    {formatType(opp.event_type)} · <strong style={{ color: 'var(--text-primary)' }}>{formatCurrency(opp.revenue_at_risk)}</strong>
                  </span>
                  
                  {isBlocked ? (
                    <span className="badge badge-danger" style={{ fontSize: '0.68rem', padding: '2px 6px' }}>
                      <ShieldAlert size={10} /> BLOCKED
                    </span>
                  ) : (
                    <span className="badge badge-success" style={{ fontSize: '0.68rem', padding: '2px 6px' }}>
                      <ShieldCheck size={10} /> APPROVED
                    </span>
                  )}
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <span className="badge badge-blue" style={{ fontFamily: 'var(--font-mono)', fontSize: '0.7rem', padding: '2px 6px' }}>
                    {opp.suggested_action}
                  </span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    {opp.event_id}
                  </span>
                </div>

                <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.35 }}>
                  "{opp.likely_root_cause !== 'UNKNOWN' ? `Diagnosed ${opp.likely_root_cause.replace(/_/g, ' ')}.` : 'Standard opportunity.'} Recoverability estimated at {Math.round(opp.recoverability_probability * 100)}%."
                </p>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
