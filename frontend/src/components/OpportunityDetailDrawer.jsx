import React, { useState, useEffect } from 'react';
import { 
  X, ShieldCheck, ShieldAlert, Bot, CheckCircle2, 
  XCircle, Play, AlertTriangle, ArrowRight, CornerDownRight 
} from 'lucide-react';
import { api } from '../services/api';

export default function OpportunityDetailDrawer({ eventId, onClose, onWorkflowExecuted }) {
  const [opportunity, setOpportunity] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [executionResult, setExecutionResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!eventId) return;

    setLoading(true);
    setError(null);

    Promise.all([
      api.getRevenueOpportunityDetail(eventId),
      api.getAIRecommendation(eventId)
    ])
      .then(([oppData, recData]) => {
        setOpportunity(oppData);
        setRecommendation(recData.recommendation);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load opportunity drawer data:', err);
        setError(err.message);
        setLoading(false);
      });
  }, [eventId]);

  const handleRunSimulation = (forceOutcome = null) => {
    setExecuting(true);
    api.executeRecoverySimulation(eventId, { force_outcome: forceOutcome })
      .then((res) => {
        setExecutionResult(res);
        setExecuting(false);
        if (onWorkflowExecuted) onWorkflowExecuted();
      })
      .catch((err) => {
        console.error('Simulation failed:', err);
        alert(`Simulation Error: ${err.message}`);
        setExecuting(false);
      });
  };

  if (!eventId) return null;

  return (
    <div className="drawer-backdrop" onClick={onClose}>
      <div className="drawer-content" onClick={(e) => e.stopPropagation()}>
        
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px', paddingBottom: '16px', borderBottom: '1px solid var(--border-color)' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <span className="badge badge-neutral" style={{ fontFamily: 'var(--font-mono)' }}>
                {eventId}
              </span>
              <span className="badge badge-blue">
                {opportunity?.event_type?.replace('_', ' ')}
              </span>
            </div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700 }}>Revenue Recovery Opportunity</h2>
          </div>
          <button className="btn-secondary" style={{ padding: '6px' }} onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        {/* 4-Step Workflow Stepper Bar */}
        <div style={{ display: 'flex', justifyContent: 'space-between', background: 'var(--bg-subtle)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '10px 14px', marginBottom: '24px', fontSize: '0.75rem', fontWeight: 600 }}>
          <div style={{ color: 'var(--razorpay-blue)', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: '18px', height: '18px', borderRadius: '50%', background: 'var(--razorpay-blue)', color: 'white', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.68rem' }}>1</span> Leak Analysis
          </div>
          <span style={{ color: 'var(--text-muted)' }}>→</span>
          <div style={{ color: recommendation ? 'var(--purple-accent)' : 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: '18px', height: '18px', borderRadius: '50%', background: recommendation ? 'var(--purple-accent)' : '#94A3B8', color: 'white', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.68rem' }}>2</span> AI Recommendation
          </div>
          <span style={{ color: 'var(--text-muted)' }}>→</span>
          <div style={{ color: executionResult ? (executionResult.guardrail.allowed ? 'var(--success-green)' : 'var(--danger-red)') : 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: '18px', height: '18px', borderRadius: '50%', background: executionResult ? (executionResult.guardrail.allowed ? 'var(--success-green)' : 'var(--danger-red)') : '#94A3B8', color: 'white', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.68rem' }}>3</span> Policy Check
          </div>
          <span style={{ color: 'var(--text-muted)' }}>→</span>
          <div style={{ color: executionResult?.outcome ? 'var(--success-green)' : 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: '18px', height: '18px', borderRadius: '50%', background: executionResult?.outcome ? 'var(--success-green)' : '#94A3B8', color: 'white', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.68rem' }}>4</span> Outcome
          </div>
        </div>

        {loading && <p style={{ color: 'var(--text-muted)' }}>Loading opportunity diagnostics...</p>}
        {error && <p style={{ color: 'var(--danger-red)' }}>Error: {error}</p>}

        {opportunity && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            
            {/* 1. Core Financial Metrics Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px' }}>
              <div style={{ background: 'var(--bg-subtle)', padding: '12px 16px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 600 }}>REVENUE AT RISK</span>
                <p style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '4px' }}>
                  ₹{Number(opportunity.revenue_at_risk).toLocaleString('en-IN')}
                </p>
              </div>

              <div style={{ background: 'var(--bg-subtle)', padding: '12px 16px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 600 }}>RECOVERABILITY</span>
                <p style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--success-green)', marginTop: '4px' }}>
                  {Math.round(opportunity.recoverability_probability * 100)}%
                </p>
              </div>

              <div style={{ background: 'var(--bg-subtle)', padding: '12px 16px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 600 }}>EXPECTED RECOVERY</span>
                <p style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--razorpay-blue)', marginTop: '4px' }}>
                  ₹{Number(opportunity.expected_recoverable_value).toLocaleString('en-IN')}
                </p>
              </div>
            </div>

            {/* 2. "Why is this opportunity prioritized?" Explanation */}
            <div className="card" style={{ padding: '16px' }}>
              <h3 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '10px' }}>
                Why is this opportunity prioritized?
              </h3>
              <ul style={{ listStyleType: 'none', display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.85rem' }}>
                <li style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)' }}>
                  <CheckCircle2 size={16} color="var(--success-green)" />
                  Likely Root Cause: <strong>{opportunity.likely_root_cause}</strong>
                </li>
                <li style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)' }}>
                  <CheckCircle2 size={16} color="var(--success-green)" />
                  Calculated Priority Score: <strong>{(opportunity.priority_score * 100).toFixed(1)} / 100</strong>
                </li>
                <li style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)' }}>
                  <CheckCircle2 size={16} color="var(--success-green)" />
                  Calculated Urgency Score: <strong>{(opportunity.urgency_score * 100).toFixed(1)}%</strong> ({opportunity.days_ago} days old)
                </li>
              </ul>
            </div>

            {/* 3. AI Recommendation Card */}
            {recommendation && (
              <div style={{ background: 'var(--razorpay-light-blue)', border: '1px solid #BFDBFE', borderRadius: '10px', padding: '18px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <Bot size={18} color="var(--razorpay-blue)" />
                  <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--razorpay-blue)' }}>
                    AI NEXT-BEST ACTION RECOMMENDATION
                  </span>
                </div>
                
                <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--razorpay-navy)', marginBottom: '8px' }}>
                  {recommendation.recommended_action}
                </div>

                <p style={{ fontSize: '0.88rem', color: 'var(--text-primary)', lineHeight: 1.5, marginBottom: '12px' }}>
                  "{recommendation.reason}"
                </p>

                <div style={{ display: 'flex', gap: '16px', fontSize: '0.78rem', color: 'var(--text-secondary)', borderTop: '1px solid #DBEAFE', paddingTop: '8px' }}>
                  <span>Confidence: <strong>{Math.round(recommendation.confidence * 100)}%</strong></span>
                  <span>Alternative: <strong>{recommendation.alternative_action}</strong></span>
                  <span>Source: <strong>{recommendation.recommendation_source}</strong></span>
                </div>
              </div>
            )}

            {/* 4. Execution Controller & Simulation Results */}
            {!executionResult ? (
              <div style={{ border: '1px solid var(--border-color)', borderRadius: '10px', padding: '18px', background: 'white' }}>
                <h4 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: '8px', color: 'var(--text-primary)' }}>
                  Policy Guardrail & Bounded Execution Control
                </h4>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginBottom: '16px' }}>
                  Clicking below will pass the AI recommendation through the merchant policy guardrail firewall and execute a SIMULATED recovery step.
                </p>

                <div style={{ display: 'flex', gap: '10px' }}>
                  <button 
                    className="btn-action" 
                    onClick={() => handleRunSimulation()}
                    disabled={executing}
                    style={{ flex: 1, padding: '10px 16px' }}
                  >
                    <Play size={16} /> {executing ? 'Executing Simulation...' : 'Run Recovery Simulation'}
                  </button>

                  <button 
                    className="btn-secondary" 
                    onClick={() => handleRunSimulation('RECOVERED')}
                    disabled={executing}
                    style={{ fontSize: '0.78rem' }}
                  >
                    Force Success
                  </button>
                </div>
              </div>
            ) : (
              <div style={{ 
                border: `1px solid ${executionResult.guardrail.allowed ? 'var(--success-border)' : 'var(--danger-border)'}`, 
                background: executionResult.guardrail.allowed ? 'var(--success-bg)' : 'var(--danger-bg)', 
                borderRadius: '10px', 
                padding: '18px' 
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
                  {executionResult.guardrail.allowed ? (
                    <ShieldCheck size={20} color="var(--success-green)" />
                  ) : (
                    <ShieldAlert size={20} color="var(--danger-red)" />
                  )}
                  <h4 style={{ fontSize: '1rem', fontWeight: 700, color: executionResult.guardrail.allowed ? 'var(--success-green)' : 'var(--danger-red)' }}>
                    {executionResult.guardrail.allowed ? 'Workflow Executed (SIMULATED)' : 'Workflow BLOCKED by Policy Guardrail'}
                  </h4>
                </div>

                <p style={{ fontSize: '0.88rem', marginBottom: '12px', color: 'var(--text-primary)' }}>
                  <strong>Guardrail Reason:</strong> {executionResult.guardrail.reason}
                </p>

                {executionResult.outcome && (
                  <div style={{ background: 'white', padding: '12px', borderRadius: '6px', border: '1px solid var(--border-color)', marginBottom: '12px' }}>
                    <p style={{ fontSize: '0.85rem' }}>
                      Simulated Outcome: <strong>{executionResult.outcome.status}</strong>
                    </p>
                    <p style={{ fontSize: '0.85rem', marginTop: '4px' }}>
                      Recovered Amount: <strong>₹{Number(executionResult.outcome.recovered_amount).toLocaleString('en-IN')}</strong>
                    </p>
                  </div>
                )}

                <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                  <strong>Why did the workflow stop?</strong> {executionResult.workflow.stop_reason}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
