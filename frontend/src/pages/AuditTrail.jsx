import React, { useState, useEffect } from 'react';
import { Search, Filter } from 'lucide-react';
import AuditTimeline from '../components/AuditTimeline';
import { api } from '../services/api';

export default function AuditTrail() {
  const [auditLogs, setAuditLogs] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterResult, setFilterResult] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Phase 6.2 Fix #1: Fetch actual database audit records via GET /api/audit-logs
    api.getAuditLogs({ limit: 200 })
      .then(data => {
        setAuditLogs(data || []);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load real audit logs:', err);
        setError('Unable to load database audit records.');
        setLoading(false);
      });
  }, []);

  const filteredLogs = auditLogs.filter(log => {
    const matchesSearch = 
      (log.revenue_event_id || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (log.reason || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (log.action || '').toLowerCase().includes(searchTerm.toLowerCase());

    const matchesResult = filterResult ? (log.guardrail_result || '').includes(filterResult) : true;
    return matchesSearch && matchesResult;
  });

  return (
    <div className="page-container" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Search & Filter Toolbar */}
      <div className="card" style={{ padding: '16px 24px', display: 'flex', gap: '16px', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ position: 'relative', width: '320px' }}>
          <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '10px' }} />
          <input 
            type="text"
            placeholder="Search Event ID, Action or Reason..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ width: '100%', paddingLeft: '36px' }}
          />
        </div>

        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <Filter size={14} color="var(--text-secondary)" />
          <select value={filterResult} onChange={(e) => setFilterResult(e.target.value)}>
            <option value="">All Guardrail Results</option>
            <option value="AI_RECOMMENDATION">AI Recommendations</option>
            <option value="PASSED">Passed Checks</option>
            <option value="BLOCKED">Blocked Violations</option>
            <option value="OUTCOME">Outcomes</option>
          </select>
        </div>
      </div>

      {/* Main Audit Trail Timeline */}
      {loading ? (
        <p style={{ color: 'var(--text-muted)' }}>Loading real database audit records...</p>
      ) : error ? (
        <div className="card" style={{ padding: '24px', color: 'var(--danger-red)' }}>
          {error}
        </div>
      ) : auditLogs.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '32px', color: 'var(--text-muted)' }}>
          No audit activity yet.
        </div>
      ) : (
        <AuditTimeline auditLogs={filteredLogs} />
      )}

    </div>
  );
}
