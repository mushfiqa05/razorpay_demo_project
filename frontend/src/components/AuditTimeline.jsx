import React from 'react';
import { History, ShieldCheck, ShieldAlert, Bot, Play, CheckCircle2 } from 'lucide-react';

export default function AuditTimeline({ auditLogs }) {
  if (!auditLogs || auditLogs.length === 0) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '32px', color: 'var(--text-muted)' }}>
        No audit log records available.
      </div>
    );
  }

  const getLogIcon = (result) => {
    if (result.includes('PASSED') || result.includes('SUCCESS') || result.includes('RECOVERED')) {
      return <ShieldCheck size={16} color="var(--success-green)" />;
    } else if (result.includes('BLOCKED') || result.includes('FAILED')) {
      return <ShieldAlert size={16} color="var(--danger-red)" />;
    } else if (result.includes('AI_RECOMMENDATION')) {
      return <Bot size={16} color="var(--razorpay-blue)" />;
    }
    return <Play size={16} color="var(--purple-accent)" />;
  };

  return (
    <div className="card">
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
        <History size={18} color="var(--razorpay-navy)" />
        <h3 className="title-medium">System Audit & Policy Decision Ledger</h3>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', position: 'relative', paddingLeft: '12px' }}>
        {auditLogs.map((log, index) => (
          <div key={log.id || index} style={{ display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
            
            {/* Timeline Icon Node */}
            <div style={{ 
              width: '28px', 
              height: '28px', 
              borderRadius: '50%', 
              background: 'var(--bg-subtle)', 
              border: '1px solid var(--border-color)', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              flexShrink: 0,
              marginTop: '2px'
            }}>
              {getLogIcon(log.guardrail_result || '')}
            </div>

            {/* Content Payload */}
            <div style={{ flex: 1, background: 'var(--bg-subtle)', padding: '12px 16px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                <span className="badge badge-neutral" style={{ fontFamily: 'var(--font-mono)', fontSize: '0.7rem' }}>
                  {log.event_id || log.revenue_event_id}
                </span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  {new Date(log.timestamp).toLocaleString()}
                </span>
              </div>

              <p style={{ fontSize: '0.88rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '4px' }}>
                Action: <span style={{ color: 'var(--razorpay-blue)' }}>{log.action}</span> | Result: {log.guardrail_result}
              </p>

              <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                {log.reason}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
