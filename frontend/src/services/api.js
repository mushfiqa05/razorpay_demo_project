const API_BASE_URL = 'http://localhost:8000/api';

/**
 * Centralized API Service for Razorpay Revenue Recovery Control Tower
 */
export const api = {
  // System Health
  getHealth: async () => {
    const res = await fetch(`${API_BASE_URL}/health`);
    if (!res.ok) throw new Error('Backend offline');
    return res.json();
  },

  // Merchants & Policies
  getMerchants: async () => {
    const res = await fetch(`${API_BASE_URL}/merchants`);
    if (!res.ok) throw new Error('Failed to fetch merchants');
    return res.json();
  },

  // Update Merchant Policy (Phase 6.2 Fix #5)
  updateMerchantPolicy: async (merchantId, payload) => {
    const res = await fetch(`${API_BASE_URL}/merchants/${merchantId}/policy`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || 'Failed to update merchant policy');
    }
    return res.json();
  },

  // Customers
  getCustomers: async (merchantId = '') => {
    const url = merchantId ? `${API_BASE_URL}/customers?merchant_id=${merchantId}` : `${API_BASE_URL}/customers`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch customers');
    return res.json();
  },

  // Raw Revenue Events
  getRevenueEvents: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    const res = await fetch(`${API_BASE_URL}/revenue-events?${query}`);
    if (!res.ok) throw new Error('Failed to fetch revenue events');
    return res.json();
  },

  // Revenue Opportunities Priority Queue (Phase 3)
  getRevenueOpportunities: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    const res = await fetch(`${API_BASE_URL}/revenue-opportunities?${query}`);
    if (!res.ok) throw new Error('Failed to fetch revenue opportunities');
    return res.json();
  },

  // Single Revenue Opportunity Detail (Phase 3)
  getRevenueOpportunityDetail: async (eventId) => {
    const res = await fetch(`${API_BASE_URL}/revenue-opportunities/${eventId}`);
    if (!res.ok) throw new Error(`Failed to fetch opportunity '${eventId}'`);
    return res.json();
  },

  // Generate AI Recommendation (Phase 4)
  getAIRecommendation: async (eventId) => {
    const res = await fetch(`${API_BASE_URL}/revenue-opportunities/${eventId}/recommendation`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    if (!res.ok) throw new Error(`Failed to generate recommendation for '${eventId}'`);
    return res.json();
  },

  // Execute Bounded Recovery Simulation Step (Phase 5)
  executeRecoverySimulation: async (eventId, payload = {}) => {
    const res = await fetch(`${API_BASE_URL}/revenue-opportunities/${eventId}/execute-recovery`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `Failed to execute recovery for '${eventId}'`);
    }
    return res.json();
  },

  // Real Database Audit Logs (Phase 6.2 Fix #1)
  getAuditLogs: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    const res = await fetch(`${API_BASE_URL}/audit-logs?${query}`);
    if (!res.ok) throw new Error('Failed to fetch audit logs');
    return res.json();
  },

  // Real Database Recovery Attempts (Phase 6.2 Fix #6)
  getRecoveryAttempts: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    const res = await fetch(`${API_BASE_URL}/recovery-attempts?${query}`);
    if (!res.ok) throw new Error('Failed to fetch recovery attempts');
    return res.json();
  }
};
