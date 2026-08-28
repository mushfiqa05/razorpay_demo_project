import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

export default function RiskBreakdownChart({ opportunities }) {
  // Aggregate revenue at risk by event type
  const breakdown = {
    'PAYMENT_FAILURE': 0,
    'CHECKOUT_ABANDONMENT': 0,
    'SUBSCRIPTION_FAILURE': 0,
    'OVERDUE_INVOICE': 0
  };

  (opportunities || []).forEach(opp => {
    if (breakdown[opp.event_type] !== undefined) {
      breakdown[opp.event_type] += opp.revenue_at_risk || 0;
    }
  });

  const data = [
    { name: 'Payment Failures', key: 'PAYMENT_FAILURE', amount: breakdown['PAYMENT_FAILURE'], color: '#0C6CF2' },
    { name: 'Checkout Abandonment', key: 'CHECKOUT_ABANDONMENT', amount: breakdown['CHECKOUT_ABANDONMENT'], color: '#F59E0B' },
    { name: 'Subscriptions', key: 'SUBSCRIPTION_FAILURE', amount: breakdown['SUBSCRIPTION_FAILURE'], color: '#8B5CF6' },
    { name: 'Overdue Invoices', key: 'OVERDUE_INVOICE', amount: breakdown['OVERDUE_INVOICE'], color: '#E53E3E' },
  ];

  const formatCurrency = (val) => {
    if (val >= 100000) return `₹${(val / 100000).toFixed(1)}L`;
    if (val >= 1000) return `₹${(val / 1000).toFixed(0)}k`;
    return `₹${val}`;
  };

  return (
    <div className="card">
      <div style={{ marginBottom: '16px' }}>
        <h3 className="title-medium">Revenue Leakage by Event Type</h3>
        <p className="text-muted" style={{ fontSize: '0.8rem', marginTop: '2px' }}>
          Distribution of revenue-at-risk across the 4 supported recovery workflows
        </p>
      </div>

      <div style={{ width: '100%', height: 260 }}>
        <ResponsiveContainer>
          <BarChart data={data} margin={{ top: 10, right: 10, left: 10, bottom: 25 }}>
            <XAxis 
              dataKey="name" 
              tick={{ fontSize: 11, fill: '#64748B' }} 
              interval={0}
            />
            <YAxis 
              tickFormatter={formatCurrency} 
              tick={{ fontSize: 11, fill: '#64748B' }} 
            />
            <Tooltip 
              formatter={(value) => [`₹${Number(value).toLocaleString('en-IN')}`, 'Revenue at Risk']}
              contentStyle={{ background: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '8px', fontSize: '0.85rem' }}
            />
            <Bar dataKey="amount" radius={[6, 6, 0, 0]}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
