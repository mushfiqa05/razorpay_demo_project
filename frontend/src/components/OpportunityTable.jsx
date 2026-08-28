import React from 'react';
import { ArrowUpRight, AlertCircle, CheckCircle2, ShieldAlert, Clock } from 'lucide-react';

export default function OpportunityTable({ opportunities, onSelectOpportunity, limit = null }) {
  const displayList = limit ? (opportunities || []).slice(0, limit) : (opportunities || []);

  const getPriorityTag = (score) => {
    if (score >= 0.70) return <span className="badge badge-danger">HIGH</span>;
    if (score >= 0.40) return <span className="badge badge-warning">MEDIUM</span>;
    return <span className="badge badge-neutral">LOW</span>;
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'RECOVERED':
        return <span className="badge badge-success"><CheckCircle2 size={12} /> RECOVERED</span>;
      case 'STOPPED':
        return <span className="badge badge-warning"><ShieldAlert size={12} /> STOPPED</span>;
      case 'FAILED':
        return <span className="badge badge-danger"><AlertCircle size={12} /> FAILED</span>;
      default:
        return <span className="badge badge-blue"><Clock size={12} /> READY</span>;
    }
  };

  const formatEventType = (type) => {
    switch (type) {
      case 'PAYMENT_FAILURE': return 'Payment Failure';
      case 'CHECKOUT_ABANDONMENT': return 'Checkout Abandonment';
      case 'SUBSCRIPTION_FAILURE': return 'Subscription Failure';
      case 'OVERDUE_INVOICE': return 'Overdue Invoice';
      default: return type;
    }
  };

  return (
    <div className="table-container">
      <table>
        <thead>
          <tr>
            <th>Priority</th>
            <th>Event ID</th>
            <th>Workflow Type</th>
            <th>Revenue at Risk</th>
            <th>Recoverability</th>
            <th>Expected Recovery</th>
            <th>Recommended Action</th>
            <th>Status</th>
            <th style={{ textAlign: 'right' }}>Action</th>
          </tr>
        </thead>
        <tbody>
          {displayList.length === 0 ? (
            <tr>
              <td colSpan="9" style={{ textAlign: 'center', padding: '32px', color: 'var(--text-muted)' }}>
                No active recovery opportunities found.
              </td>
            </tr>
          ) : (
            displayList.map((opp) => (
              <tr key={opp.event_id} style={{ cursor: 'pointer' }} onClick={() => onSelectOpportunity(opp.event_id)}>
                <td>{getPriorityTag(opp.priority_score)}</td>
                <td>
                  <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{opp.event_id}</span>
                </td>
                <td style={{ fontWeight: 500 }}>{formatEventType(opp.event_type)}</td>
                <td style={{ fontWeight: 600 }}>
                  ₹{Number(opp.revenue_at_risk).toLocaleString('en-IN')}
                </td>
                <td>
                  <span style={{ 
                    fontWeight: 600, 
                    color: opp.recoverability_probability >= 0.7 ? 'var(--success-green)' : opp.recoverability_probability < 0.3 ? 'var(--danger-red)' : 'var(--text-primary)'
                  }}>
                    {Math.round(opp.recoverability_probability * 100)}%
                  </span>
                </td>
                <td style={{ fontWeight: 700, color: 'var(--razorpay-navy)' }}>
                  ₹{Number(opp.expected_recoverable_value).toLocaleString('en-IN')}
                </td>
                <td>
                  <span className="badge badge-neutral" style={{ fontFamily: 'var(--font-mono)', fontSize: '0.72rem' }}>
                    {opp.suggested_action}
                  </span>
                </td>
                <td>{getStatusBadge(opp.status)}</td>
                <td style={{ textAlign: 'right' }}>
                  <button 
                    className="btn-secondary"
                    style={{ padding: '4px 10px', fontSize: '0.78rem' }}
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelectOpportunity(opp.event_id);
                    }}
                  >
                    Inspect <ArrowUpRight size={14} />
                  </button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
