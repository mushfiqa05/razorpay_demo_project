import React from 'react';
import { Zap, Clock, ShieldAlert, ArrowRight } from 'lucide-react';

export default function RecoveryCommandCenter({ opportunities, onSelectOpportunity }) {
  const oppList = opportunities || [];

  // 1. Identify Highest Recovery Opportunity (Max expected_recoverable_value)
  const highestOpp = oppList.length > 0 
    ? [...oppList].sort((a, b) => (b.expected_recoverable_value || 0) - (a.expected_recoverable_value || 0))[0] 
    : null;

  // 2. Identify Most Urgent Opportunity (Max urgency_score or age)
  const mostUrgentOpp = oppList.length > 0 
    ? [...oppList].sort((a, b) => (b.urgency_score || 0) - (a.urgency_score || 0))[0] 
    : null;

  // 3. Identify Blocked by Policy Opportunity (Phase 6.2 Fix #7: Strictly STOPPED or FAILED backend status)
  const blockedOpp = oppList.find(o => o.status === 'STOPPED' || o.status === 'FAILED') || null;

  const formatCurrency = (val) => `₹${Number(val || 0).toLocaleString('en-IN')}`;

  const formatType = (type) => {
    switch (type) {
      case 'PAYMENT_FAILURE': return 'Payment Failure';
      case 'CHECKOUT_ABANDONMENT': return 'Checkout Abandonment';
      case 'SUBSCRIPTION_FAILURE': return 'Subscription Failure';
      case 'OVERDUE_INVOICE': return 'Overdue Invoice';
      default: return type || 'Revenue Leak';
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div>
        <h2 className="title-medium" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Zap size={18} color="var(--razorpay-blue)" /> Recovery Command Center
        </h2>
        <p className="text-muted" style={{ fontSize: '0.82rem', marginTop: '2px' }}>
          Focus on high-ROI interventions and policy blocked events requiring immediate attention.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
        
        {/* INSIGHT CARD 1: HIGHEST OPPORTUNITY */}
        <div className="card" style={{ borderLeft: '4px solid var(--razorpay-blue)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--razorpay-blue)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Highest Recovery Potential
              </span>
              <span className="badge badge-blue">{highestOpp ? `${Math.round(highestOpp.recoverability_probability * 100)}% Rec.` : 'N/A'}</span>
            </div>

            {highestOpp ? (
              <>
                <h3 style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '2px' }}>
                  {formatCurrency(highestOpp.revenue_at_risk)}
                </h3>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 500, marginBottom: '12px' }}>
                  {formatType(highestOpp.event_type)} · {highestOpp.event_id}
                </p>

                <div style={{ background: 'var(--bg-subtle)', padding: '10px 12px', borderRadius: '6px', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '16px' }}>
                  <div>Expected Recovery: <strong style={{ color: 'var(--razorpay-navy)' }}>{formatCurrency(highestOpp.expected_recoverable_value)}</strong></div>
                  <div>Recommended: <strong style={{ color: 'var(--razorpay-blue)' }}>{highestOpp.suggested_action}</strong></div>
                </div>
              </>
            ) : (
              <p className="text-muted" style={{ padding: '16px 0' }}>No active recovery opportunities.</p>
            )}
          </div>

          {highestOpp && (
            <button 
              className="btn-secondary" 
              style={{ width: '100%', justifyContent: 'center', padding: '8px', fontSize: '0.82rem' }}
              onClick={() => onSelectOpportunity(highestOpp.event_id)}
            >
              View Opportunity <ArrowRight size={14} />
            </button>
          )}
        </div>

        {/* INSIGHT CARD 2: MOST URGENT */}
        <div className="card" style={{ borderLeft: '4px solid var(--warning-amber)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--warning-amber)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Most Urgent Recovery
              </span>
              <span className="badge badge-warning">
                <Clock size={12} /> {mostUrgentOpp ? `${Math.round(mostUrgentOpp.urgency_score * 100)}% Urgency` : 'N/A'}
              </span>
            </div>

            {mostUrgentOpp ? (
              <>
                <h3 style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '2px' }}>
                  {formatCurrency(mostUrgentOpp.revenue_at_risk)}
                </h3>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 500, marginBottom: '12px' }}>
                  {formatType(mostUrgentOpp.event_type)} · {mostUrgentOpp.days_ago}d ago
                </p>

                <div style={{ background: 'var(--bg-subtle)', padding: '10px 12px', borderRadius: '6px', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '16px' }}>
                  <div>Root Cause: <strong>{mostUrgentOpp.likely_root_cause}</strong></div>
                  <div>Recommended: <strong style={{ color: 'var(--warning-amber)' }}>{mostUrgentOpp.suggested_action}</strong></div>
                </div>
              </>
            ) : (
              <p className="text-muted" style={{ padding: '16px 0' }}>No urgent recovery tasks.</p>
            )}
          </div>

          {mostUrgentOpp && (
            <button 
              className="btn-secondary" 
              style={{ width: '100%', justifyContent: 'center', padding: '8px', fontSize: '0.82rem' }}
              onClick={() => onSelectOpportunity(mostUrgentOpp.event_id)}
            >
              Action Urgent Leak <ArrowRight size={14} />
            </button>
          )}
        </div>

        {/* INSIGHT CARD 3: BLOCKED BY POLICY */}
        <div className="card" style={{ borderLeft: '4px solid var(--danger-red)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--danger-red)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Blocked by Guardrail
              </span>
              <span className="badge badge-danger">
                <ShieldAlert size={12} /> Policy Block
              </span>
            </div>

            {blockedOpp ? (
              <>
                <h3 style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '2px' }}>
                  {formatCurrency(blockedOpp.revenue_at_risk)}
                </h3>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 500, marginBottom: '12px' }}>
                  {formatType(blockedOpp.event_type)} · {blockedOpp.event_id}
                </p>

                <div style={{ background: 'var(--danger-bg)', border: '1px solid var(--danger-border)', padding: '10px 12px', borderRadius: '6px', fontSize: '0.8rem', color: 'var(--danger-red)', marginBottom: '16px' }}>
                  <div>Attempted: <strong>{blockedOpp.suggested_action}</strong></div>
                  <div style={{ marginTop: '2px', fontSize: '0.75rem' }}>
                    Status: {blockedOpp.status} (Max attempts, reminder limit, or opt-out)
                  </div>
                </div>
              </>
            ) : (
              <div style={{ padding: '16px 0', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                ✓ No policy guardrail blocks recorded in current period.
              </div>
            )}
          </div>

          {blockedOpp && (
            <button 
              className="btn-secondary" 
              style={{ width: '100%', justifyContent: 'center', padding: '8px', fontSize: '0.82rem' }}
              onClick={() => onSelectOpportunity(blockedOpp.event_id)}
            >
              Inspect Policy Firewall <ArrowRight size={14} />
            </button>
          )}
        </div>

      </div>
    </div>
  );
}
