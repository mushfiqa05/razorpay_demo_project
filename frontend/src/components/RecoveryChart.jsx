import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

export default function RecoveryChart({ opportunities }) {
  const counts = {
    'RECOVERED': 0,
    'OPEN': 0,
    'IN_RECOVERY': 0,
    'FAILED': 0,
    'STOPPED': 0
  };

  (opportunities || []).forEach(opp => {
    const st = opp.status || 'OPEN';
    counts[st] = (counts[st] || 0) + 1;
  });

  // Phase 6.2 Fix #2: Pure data representation with 0 fake metric fallbacks
  const data = [
    { name: 'Recovered', value: counts['RECOVERED'] || 0, color: '#10B981' },
    { name: 'Open (Ready)', value: counts['OPEN'] || 0, color: '#0C6CF2' },
    { name: 'In Recovery', value: counts['IN_RECOVERY'] || 0, color: '#8B5CF6' },
    { name: 'Stopped / Blocked', value: counts['STOPPED'] || 0, color: '#F59E0B' },
    { name: 'Failed', value: counts['FAILED'] || 0, color: '#EF4444' },
  ].filter(item => item.value > 0); // Only render categories that actually exist

  return (
    <div className="card">
      <div style={{ marginBottom: '16px' }}>
        <h3 className="title-medium">Recovery Workflow Outcomes</h3>
        <p className="text-muted" style={{ fontSize: '0.8rem', marginTop: '2px' }}>
          Current execution status breakdown across active opportunities
        </p>
      </div>

      {data.length === 0 ? (
        <div style={{ padding: '32px', textAlign: 'center', color: 'var(--text-muted)' }}>
          No workflow outcomes recorded yet.
        </div>
      ) : (
        <div style={{ width: '100%', height: 260 }}>
          <ResponsiveContainer>
            <PieChart>
              <Pie
                data={data}
                innerRadius={55}
                outerRadius={85}
                paddingAngle={4}
                dataKey="value"
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ background: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '8px', fontSize: '0.85rem' }}
              />
              <Legend 
                verticalAlign="bottom" 
                height={36} 
                iconType="circle"
                formatter={(value) => <span style={{ fontSize: '0.75rem', color: '#475569' }}>{value}</span>}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
