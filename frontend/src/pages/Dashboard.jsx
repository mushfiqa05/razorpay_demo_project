import React, { useState } from 'react';
import { AlertOctagon, TrendingUp, CheckCircle, Percent } from 'lucide-react';
import KPICard from '../components/KPICard';
import ProblemSolutionBanner from '../components/ProblemSolutionBanner';
import RecoveryCommandCenter from '../components/RecoveryCommandCenter';
import RiskBreakdownChart from '../components/RiskBreakdownChart';
import AIDecisionFeed from '../components/AIDecisionFeed';
import PriorityExplanationCard from '../components/PriorityExplanationCard';
import RecoveryChart from '../components/RecoveryChart';
import OpportunityTable from '../components/OpportunityTable';

export default function Dashboard({ opportunities, onSelectOpportunity, onNavigateToOpportunities }) {
  const [activeWorkflowTab, setActiveWorkflowTab] = useState('ALL');
  
  const oppList = (opportunities || []).filter(o => {
    if (activeWorkflowTab === 'ALL') return true;
    return o.event_type === activeWorkflowTab;
  });

  // Calculate dynamic KPI statistics directly from backend API data (Phase 6.2 Fix #2: Zero business fallbacks)
  const totalRisk = oppList.reduce((acc, curr) => acc + (curr.revenue_at_risk || 0), 0);
  const totalExpected = oppList.reduce((acc, curr) => acc + (curr.expected_recoverable_value || 0), 0);
  
  const recoveredList = oppList.filter(o => o.status === 'RECOVERED');
  const totalRecovered = recoveredList.reduce((acc, curr) => acc + (curr.revenue_at_risk || 0), 0);
  
  const expectedPctOfRisk = totalRisk > 0 ? Math.round((totalExpected / totalRisk) * 100) : 0;
  const recoveryRate = totalExpected > 0 ? ((totalRecovered / totalExpected) * 100).toFixed(1) : '0.0';

  const formatLakhs = (val) => {
    if (val >= 100000) return `₹${(val / 100000).toFixed(2)}L`;
    return `₹${val.toLocaleString('en-IN')}`;
  };

  const workflowTabs = [
    { id: 'ALL', label: 'All Revenue Leaks', count: (opportunities || []).length },
    { id: 'PAYMENT_FAILURE', label: 'Payment Failures', count: (opportunities || []).filter(o => o.event_type === 'PAYMENT_FAILURE').length },
    { id: 'CHECKOUT_ABANDONMENT', label: 'Checkout Abandonments', count: (opportunities || []).filter(o => o.event_type === 'CHECKOUT_ABANDONMENT').length },
    { id: 'SUBSCRIPTION_FAILURE', label: 'Subscriptions', count: (opportunities || []).filter(o => o.event_type === 'SUBSCRIPTION_FAILURE').length },
    { id: 'OVERDUE_INVOICE', label: 'Overdue Invoices', count: (opportunities || []).filter(o => o.event_type === 'OVERDUE_INVOICE').length },
  ];

  return (
    <div className="page-container" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Visual Problem-to-Solution Architecture Banner */}
      <ProblemSolutionBanner />

      {/* Workflow Filter Selector Tabs */}
      <div style={{ display: 'flex', gap: '8px', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px', overflowX: 'auto' }}>
        {workflowTabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveWorkflowTab(tab.id)}
            style={{
              padding: '6px 14px',
              borderRadius: '20px',
              fontSize: '0.82rem',
              fontWeight: activeWorkflowTab === tab.id ? 700 : 500,
              background: activeWorkflowTab === tab.id ? 'var(--razorpay-navy)' : 'white',
              color: activeWorkflowTab === tab.id ? 'white' : 'var(--text-secondary)',
              border: activeWorkflowTab === tab.id ? '1px solid var(--razorpay-navy)' : '1px solid var(--border-color)',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            {tab.label}
            <span style={{ 
              background: activeWorkflowTab === tab.id ? 'rgba(255,255,255,0.2)' : 'var(--bg-subtle)', 
              color: activeWorkflowTab === tab.id ? 'white' : 'var(--text-muted)',
              padding: '2px 6px',
              borderRadius: '10px',
              fontSize: '0.7rem'
            }}>
              {tab.count}
            </span>
          </button>
        ))}
      </div>

      {/* LEVEL 1: KPI SUMMARY CARDS */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '20px' }}>
        <KPICard 
          title="Revenue at Risk" 
          value={formatLakhs(totalRisk)}
          subtext={`${oppList.length} active leaks · ${formatLakhs(totalExpected)} recoverable`}
          icon={AlertOctagon}
          color="coral"
        />

        <KPICard 
          title="Expected Recoverable" 
          value={formatLakhs(totalExpected)}
          subtext={`${expectedPctOfRisk}% of revenue-at-risk`}
          icon={TrendingUp}
          color="blue"
        />

        <KPICard 
          title="Recovered Revenue" 
          value={formatLakhs(totalRecovered)}
          subtext="Captured from simulated recoveries"
          icon={CheckCircle}
          color="green"
        />

        <KPICard 
          title="Recovery Success Rate" 
          value={`${recoveryRate}%`}
          subtext="Recovered / Expected ratio"
          icon={Percent}
          color="amber"
        />
      </div>

      {/* LEVEL 2: RECOVERY COMMAND CENTER (3 Operational Insight Cards) */}
      <RecoveryCommandCenter 
        opportunities={oppList} 
        onSelectOpportunity={onSelectOpportunity} 
      />

      {/* LEVEL 3 & 4: OPPORTUNITY MAP & AI DECISION FEED GRID */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '24px', alignItems: 'stretch' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <RiskBreakdownChart opportunities={oppList} />
          <PriorityExplanationCard />
        </div>

        <div>
          <AIDecisionFeed 
            opportunities={oppList} 
            onSelectOpportunity={onSelectOpportunity} 
          />
        </div>
      </div>

      {/* LEVEL 5: PRIORITY OPPORTUNITIES QUEUE */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <div>
            <h2 className="title-medium">Priority Recovery Opportunities Queue</h2>
            <p className="text-muted" style={{ fontSize: '0.8rem', marginTop: '2px' }}>
              Ranked dynamically by Expected Recoverable Value and urgency metrics
            </p>
          </div>
          <button className="btn-secondary" onClick={onNavigateToOpportunities}>
            View All Opportunities →
          </button>
        </div>

        <OpportunityTable 
          opportunities={oppList} 
          onSelectOpportunity={onSelectOpportunity}
          limit={7}
        />
      </div>

      {/* RECOVERY OUTCOMES PERFORMANCE */}
      <RecoveryChart opportunities={oppList} />

    </div>
  );
}
