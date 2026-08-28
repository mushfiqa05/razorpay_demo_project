import React from 'react';

export default function KPICard({ title, value, subtext, icon: Icon, color = 'blue', trend }) {
  const accentColors = {
    blue: 'var(--razorpay-blue)',
    green: 'var(--success-green)',
    amber: 'var(--warning-amber)',
    coral: 'var(--accent-coral)'
  };

  return (
    <div className="kpi-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
        <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
          {title}
        </span>
        {Icon && (
          <div style={{ 
            padding: '8px', 
            borderRadius: '6px', 
            background: 'var(--bg-subtle)',
            color: accentColors[color] || 'var(--razorpay-blue)'
          }}>
            <Icon size={18} />
          </div>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginBottom: '6px' }}>
        <h2 style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
          {value}
        </h2>
        {trend && (
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--success-green)' }}>
            {trend}
          </span>
        )}
      </div>

      {subtext && (
        <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
          {subtext}
        </p>
      )}
    </div>
  );
}
