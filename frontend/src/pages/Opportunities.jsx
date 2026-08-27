import React, { useState } from 'react';
import { Search, Filter, ArrowUpDown } from 'lucide-react';
import OpportunityTable from '../components/OpportunityTable';

export default function Opportunities({ opportunities, onSelectOpportunity }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [eventTypeFilter, setEventTypeFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [sortBy, setSortBy] = useState('priority_desc');

  // Filter opportunities list
  const filtered = (opportunities || []).filter(opp => {
    const matchesSearch = 
      opp.event_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      opp.likely_root_cause.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesType = eventTypeFilter ? opp.event_type === eventTypeFilter : true;
    const matchesStatus = statusFilter ? opp.status === statusFilter : true;

    return matchesSearch && matchesType && matchesStatus;
  });

  // Sort opportunities list
  const sorted = [...filtered].sort((a, b) => {
    if (sortBy === 'priority_desc') return b.priority_score - a.priority_score;
    if (sortBy === 'risk_desc') return b.revenue_at_risk - a.revenue_at_risk;
    if (sortBy === 'expected_desc') return b.expected_recoverable_value - a.expected_recoverable_value;
    if (sortBy === 'recoverability_desc') return b.recoverability_probability - a.recoverability_probability;
    return 0;
  });

  return (
    <div className="page-container" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Search & Filter Toolbar */}
      <div className="card" style={{ padding: '16px 24px', display: 'flex', flexWrap: 'wrap', gap: '16px', alignItems: 'center', justifyContent: 'space-between' }}>
        
        {/* Search Bar */}
        <div style={{ position: 'relative', width: '300px' }}>
          <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '10px' }} />
          <input 
            type="text"
            placeholder="Search Event ID or Root Cause..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ width: '100%', paddingLeft: '36px' }}
          />
        </div>

        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          {/* Event Type Filter */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Filter size={14} color="var(--text-secondary)" />
            <select value={eventTypeFilter} onChange={(e) => setEventTypeFilter(e.target.value)}>
              <option value="">All Workflow Types</option>
              <option value="PAYMENT_FAILURE">Payment Failure</option>
              <option value="CHECKOUT_ABANDONMENT">Checkout Abandonment</option>
              <option value="SUBSCRIPTION_FAILURE">Subscription Failure</option>
              <option value="OVERDUE_INVOICE">Overdue Invoice</option>
            </select>
          </div>

          {/* Status Filter */}
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="">All Statuses</option>
            <option value="OPEN">OPEN / Ready</option>
            <option value="IN_RECOVERY">IN RECOVERY</option>
            <option value="RECOVERED">RECOVERED</option>
            <option value="FAILED">FAILED</option>
            <option value="STOPPED">STOPPED</option>
          </select>

          {/* Sort Dropdown */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <ArrowUpDown size={14} color="var(--text-secondary)" />
            <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
              <option value="priority_desc">Sort: Priority Score (High to Low)</option>
              <option value="expected_desc">Sort: Expected Recovery (High to Low)</option>
              <option value="risk_desc">Sort: Revenue at Risk (High to Low)</option>
              <option value="recoverability_desc">Sort: Recoverability % (High to Low)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Main Opportunities Table */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h2 className="title-medium">Active Recovery Opportunities ({sorted.length})</h2>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            Showing {sorted.length} of {(opportunities || []).length} total events
          </span>
        </div>

        <OpportunityTable 
          opportunities={sorted}
          onSelectOpportunity={onSelectOpportunity}
        />
      </div>

    </div>
  );
}
