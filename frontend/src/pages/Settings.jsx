import React, { useState, useEffect } from 'react';
import { Settings as SettingsIcon, Save, Check, AlertCircle } from 'lucide-react';
import { api } from '../services/api';

export default function Settings({ merchant }) {
  const merchantId = merchant?.id || 'MERCH-URBANKART';

  const [maxAttempts, setMaxAttempts] = useState(3);
  const [maxReminders, setMaxReminders] = useState(2);
  const [maxDiscount, setMaxDiscount] = useState(10.0);
  const [windowDays, setWindowDays] = useState(14);
  const [minRecovery, setMinRecovery] = useState(100.0);
  
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  // Sync state when merchant prop updates
  useEffect(() => {
    if (merchant?.policies) {
      const p = merchant.policies;
      setMaxAttempts(p.max_recovery_attempts ?? 3);
      setMaxReminders(p.max_reminders ?? 2);
      setMaxDiscount(Number(p.max_discount_percentage ?? 10.0));
      setWindowDays(p.recovery_window_days ?? 14);
      setMinRecovery(Number(p.minimum_expected_recovery ?? 100.0));
    }
  }, [merchant]);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSaveSuccess(false);
    setErrorMessage(null);

    // Validation
    if (maxAttempts < 1) {
      setErrorMessage('Maximum attempts must be at least 1.');
      setSaving(false);
      return;
    }

    try {
      // Phase 6.2 Fix #5: Persist merchant policy guardrails directly to PostgreSQL/SQLite DB
      const updatedPolicy = await api.updateMerchantPolicy(merchantId, {
        max_recovery_attempts: maxAttempts,
        max_reminders: maxReminders,
        max_discount_percentage: maxDiscount,
        recovery_window_days: windowDays,
        minimum_expected_recovery: minRecovery
      });

      setSaveSuccess(true);
      setSaving(false);
      setTimeout(() => setSaveSuccess(false), 4000);
    } catch (err) {
      console.error('Failed to persist policy settings:', err);
      setErrorMessage(err.message || 'Failed to persist merchant policy settings to database.');
      setSaving(false);
    }
  };

  return (
    <div className="page-container" style={{ maxWidth: '800px' }}>
      <div className="card">
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', paddingBottom: '16px', borderBottom: '1px solid var(--border-color)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <SettingsIcon size={20} color="var(--razorpay-navy)" />
            <div>
              <h2 className="title-medium">Merchant Policy Guardrail Settings</h2>
              <p className="text-muted" style={{ fontSize: '0.8rem' }}>
                Configure persistent guardrail safety limits for {merchant?.name || 'UrbanKart Retail'}
              </p>
            </div>
          </div>
          <span className="badge badge-neutral">PERSISTENT BACKEND POLICY</span>
        </div>

        {saveSuccess && (
          <div style={{ background: 'var(--success-bg)', border: '1px solid var(--success-border)', color: 'var(--success-green)', padding: '12px 16px', borderRadius: '8px', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.88rem' }}>
            <Check size={16} /> Merchant policy settings saved & persisted to database successfully! Guardrail Engine now uses these rules.
          </div>
        )}

        {errorMessage && (
          <div style={{ background: 'var(--danger-bg)', border: '1px solid var(--danger-border)', color: 'var(--danger-red)', padding: '12px 16px', borderRadius: '8px', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.88rem' }}>
            <AlertCircle size={16} /> {errorMessage}
          </div>
        )}

        <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          <div>
            <label style={{ display: 'block', fontSize: '0.88rem', fontWeight: 600, marginBottom: '6px' }}>
              Maximum Recovery Attempts per Incident
            </label>
            <input 
              type="number" 
              value={maxAttempts} 
              onChange={(e) => setMaxAttempts(Number(e.target.value))} 
              style={{ width: '100%' }}
              min="1"
              max="10"
              required
            />
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Workflows automatically halt once this limit is reached.
            </span>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.88rem', fontWeight: 600, marginBottom: '6px' }}>
              Maximum Automated Reminders
            </label>
            <input 
              type="number" 
              value={maxReminders} 
              onChange={(e) => setMaxReminders(Number(e.target.value))} 
              style={{ width: '100%' }}
              min="0"
              max="5"
              required
            />
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Caps total reminder notifications to prevent customer spam.
            </span>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.88rem', fontWeight: 600, marginBottom: '6px' }}>
              Maximum Approved Discount Incentive (%)
            </label>
            <input 
              type="number" 
              value={maxDiscount} 
              onChange={(e) => setMaxDiscount(Number(e.target.value))} 
              style={{ width: '100%' }}
              min="0"
              max="50"
              step="0.5"
              required
            />
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Hard policy limit for OFFER_APPROVED_INCENTIVE actions.
            </span>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.88rem', fontWeight: 600, marginBottom: '6px' }}>
              Recovery Window Duration (Days)
            </label>
            <input 
              type="number" 
              value={windowDays} 
              onChange={(e) => setWindowDays(Number(e.target.value))} 
              style={{ width: '100%' }}
              min="1"
              max="90"
              required
            />
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Events older than this window are blocked from automated outreach.
            </span>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.88rem', fontWeight: 600, marginBottom: '6px' }}>
              Minimum Expected Recovery Threshold (₹)
            </label>
            <input 
              type="number" 
              value={minRecovery} 
              onChange={(e) => setMinRecovery(Number(e.target.value))} 
              style={{ width: '100%' }}
              min="0"
              required
            />
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Avoids chasing low-ROI micro leaks where recovery cost exceeds value.
            </span>
          </div>

          <div style={{ paddingTop: '16px', borderTop: '1px solid var(--border-color)', display: 'flex', justifyContent: 'flex-end' }}>
            <button type="submit" className="btn-primary" disabled={saving}>
              <Save size={16} /> {saving ? 'Persisting...' : 'Save Policy Rules'}
            </button>
          </div>

        </form>

      </div>
    </div>
  );
}
