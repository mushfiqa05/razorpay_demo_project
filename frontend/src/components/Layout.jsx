import React, { useState, useEffect } from 'react';
import Sidebar from './Sidebar';
import Header from './Header';
import OpportunityDetailDrawer from './OpportunityDetailDrawer';
import Dashboard from '../pages/Dashboard';
import Opportunities from '../pages/Opportunities';
import RecoveryActivity from '../pages/RecoveryActivity';
import AuditTrail from '../pages/AuditTrail';
import Settings from '../pages/Settings';
import { api } from '../services/api';

export default function Layout() {
  const [currentPage, setCurrentPage] = useState('overview');
  const [merchants, setMerchants] = useState([]);
  const [selectedMerchantId, setSelectedMerchantId] = useState('');
  const [opportunities, setOpportunities] = useState([]);
  const [selectedEventId, setSelectedEventId] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState(null);

  // Load merchants on initial render
  useEffect(() => {
    api.getMerchants()
      .then((data) => {
        setMerchants(data);
        if (data.length > 0) {
          setSelectedMerchantId(data[0].id);
        }
      })
      .catch((err) => {
        console.error('Failed to load merchants:', err);
        setError('Cannot connect to backend server. Make sure uvicorn backend is running.');
      });
  }, []);

  // Fetch opportunities whenever selected merchant or refresh is triggered
  const loadOpportunitiesData = () => {
    setIsRefreshing(true);
    const params = selectedMerchantId ? { merchant_id: selectedMerchantId } : {};
    
    api.getRevenueOpportunities(params)
      .then((data) => {
        setOpportunities(data.opportunities || []);
        setIsRefreshing(false);
      })
      .catch((err) => {
        console.error('Failed to load opportunities:', err);
        setError(err.message);
        setIsRefreshing(false);
      });
  };

  useEffect(() => {
    if (selectedMerchantId) {
      loadOpportunitiesData();
    }
  }, [selectedMerchantId]);

  const selectedMerchant = merchants.find(m => m.id === selectedMerchantId) || merchants[0];

  const getPageTitle = () => {
    switch (currentPage) {
      case 'overview': return 'Revenue Recovery Control Tower';
      case 'opportunities': return 'Priority Recovery Opportunities';
      case 'activity': return 'Recovery Intervention Activity';
      case 'audit': return 'System Audit & Decision Ledger';
      case 'settings': return 'Merchant Policy Guardrails';
      default: return 'Control Tower';
    }
  };

  const getPageSubtitle = () => {
    switch (currentPage) {
      case 'overview': return 'Identify, prioritize, and recover revenue-at-risk across all 4 recovery workflows.';
      case 'opportunities': return 'Inspect expected recoverable value and trigger bounded AI recovery interventions.';
      case 'activity': return 'Track real-time simulated recovery attempts and workflow outcomes.';
      case 'audit': return 'Immutable chronological record of system decisions, AI recommendations, and policy firewalls.';
      case 'settings': return 'Manage deterministic merchant policy guardrails and contact constraints.';
      default: return '';
    }
  };

  return (
    <div className="app-layout">
      {/* Sidebar Navigation */}
      <Sidebar 
        currentPage={currentPage} 
        setCurrentPage={setCurrentPage} 
        merchantName={selectedMerchant?.name} 
      />

      {/* Main Area */}
      <div className="main-content">
        <Header 
          title={getPageTitle()}
          subtitle={getPageSubtitle()}
          merchants={merchants}
          selectedMerchantId={selectedMerchantId}
          setSelectedMerchantId={setSelectedMerchantId}
          onRefresh={loadOpportunitiesData}
          isRefreshing={isRefreshing}
        />

        {error && (
          <div style={{ margin: '24px 32px 0 32px', background: 'var(--danger-bg)', border: '1px solid var(--danger-border)', color: 'var(--danger-red)', padding: '14px 18px', borderRadius: '8px', fontSize: '0.88rem' }}>
            ⚠️ Backend Connection Notice: {error}
          </div>
        )}

        {/* Page Routing */}
        <main>
          {currentPage === 'overview' && (
            <Dashboard 
              opportunities={opportunities} 
              onSelectOpportunity={(id) => setSelectedEventId(id)}
              onNavigateToOpportunities={() => setCurrentPage('opportunities')}
            />
          )}

          {currentPage === 'opportunities' && (
            <Opportunities 
              opportunities={opportunities} 
              onSelectOpportunity={(id) => setSelectedEventId(id)}
            />
          )}

          {currentPage === 'activity' && (
            <RecoveryActivity 
              onSelectOpportunity={(id) => setSelectedEventId(id)}
            />
          )}

          {currentPage === 'audit' && (
            <AuditTrail />
          )}

          {currentPage === 'settings' && (
            <Settings 
              merchant={selectedMerchant}
            />
          )}
        </main>
      </div>

      {/* Slide-over Opportunity Detail Drawer */}
      {selectedEventId && (
        <OpportunityDetailDrawer 
          eventId={selectedEventId}
          onClose={() => setSelectedEventId(null)}
          onWorkflowExecuted={loadOpportunitiesData}
        />
      )}
    </div>
  );
}
