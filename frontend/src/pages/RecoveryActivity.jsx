import React, { useState, useEffect } from 'react';
import { Activity, ArrowUpRight } from 'lucide-react';
import { api } from '../services/api';

export default function RecoveryActivity({ onSelectOpportunity }) {
  const [attempts, setAttempts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Phase 6.2 Fix #6: Fetch actual recovery attempt execution logs from database
    api.getRecoveryAttempts({ limit: 100 })
      .then(data => {
        setAttempts(data || []);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load real recovery attempts:', err);
        setError('Unable to load recovery attempts from database.');
        setLoading(false);
      });
  }, []);

  const totalAttempts = attempts.length;
  const successfulCount = attempts.filter(a => a.status === 'SUCCESS' || a.outcome?.outcome === 'RECOVERED').length;
  const failedCount = attempts.filter(a => a.status === 'FAILED' || a.outcome?.outcome === 'FAILED').length;
  const pendingCount = attempts.filter(a => a.status === 'PENDING').length;

  return (
    <div className="page-container" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Activity Summary Tiles */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
        <div className="kpi-card">
          <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 600 }}>TOTAL ATTEMPTS</span>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginTop: '4px' }}>{totalAttempts}</h2>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Real execution attempts</span>
        </div>

        <div className="kpi-card">
          <span style={{ fontSize: '0.8rem', color: 'var(--success-green)', fontWeight: 600 }}>SUCCESSFUL RECOVERIES</span>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginTop: '4px', color: 'var(--success-green)' }}>{successfulCount}</h2>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Successful outcomes</span>
        </div>

        <div className="kpi-card">
          <span style={{ fontSize: '0.8rem', color: 'var(--purple-accent)', fontWeight: 600 }}>PENDING / IN PROGRESS</span>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginTop: '4px', color: 'var(--purple-accent)' }}>{pendingCount}</h2>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Awaiting outcome</span>
        </div>

        <div className="kpi-card">
          <span style={{ fontSize: '0.8rem', color: 'var(--danger-red)', fontWeight: 600 }}>FAILED ATTEMPTS</span>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginTop: '4px', color: 'var(--danger-red)' }}>{failedCount}</h2>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Failed executions</span>
        </div>
      </div>

      {/* Activity List Table */}
      <div className="card">
        <div style={{ marginBottom: '16px' }}>
          <h2 className="title-medium">Real Database Recovery Attempts</h2>
          <p className="text-muted" style={{ fontSize: '0.8rem', marginTop: '2px' }}>
            Actual intervention execution logs stored in database
          </p>
        </div>

        {loading ? (
          <p style={{ color: 'var(--text-muted)' }}>Loading recovery attempts...</p>
        ) : error ? (
          <p style={{ color: 'var(--danger-red)' }}>{error}</p>
        ) : attempts.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '32px', color: 'var(--text-muted)' }}>
            No recovery attempts yet.
          </div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Attempt ID</th>
                  <th>Event ID</th>
                  <th>Action Executed</th>
                  <th>Attempt #</th>
                  <th>Status</th>
                  <th>Outcome</th>
                  <th>Timestamp</th>
                  <th style={{ textAlign: 'right' }}>Inspect</th>
                </tr>
              </thead>
              <tbody>
                {attempts.map((att) => (
                  <tr key={att.id}>
                    <td>
                      <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{att.id}</span>
                    </td>
                    <td>
                      <span style={{ fontFamily: 'var(--font-mono)' }}>{att.revenue_event_id}</span>
                    </td>
                    <td style={{ fontWeight: 600 }}>{att.action_type}</td>
                    <td>Attempt {att.attempt_number}</td>
                    <td>
                      <span className={`badge badge-${att.status === 'SUCCESS' ? 'success' : att.status === 'PENDING' ? 'blue' : 'danger'}`}>
                        {att.status}
                      </span>
                    </td>
                    <td>
                      {att.outcome ? (
                        <span className={`badge badge-${att.outcome.outcome === 'RECOVERED' ? 'success' : 'danger'}`}>
                          {att.outcome.outcome} (₹{Number(att.outcome.recovered_amount).toLocaleString('en-IN')})
                        </span>
                      ) : (
                        <span className="badge badge-neutral">PENDING</span>
                      )}
                    </td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                      {new Date(att.attempted_at).toLocaleString()}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <button 
                        className="btn-secondary"
                        style={{ padding: '4px 10px', fontSize: '0.78rem' }}
                        onClick={() => onSelectOpportunity(att.revenue_event_id)}
                      >
                        Inspect <ArrowUpRight size={14} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

    </div>
  );
}
