import React from 'react';
import { X, ShieldCheck, CheckCircle2, Bot, Scale, Zap, BookOpen } from 'lucide-react';

export default function JuryGuideModal({ onClose }) {
  return (
    <div className="drawer-backdrop" onClick={onClose} style={{ zIndex: 300 }}>
      <div className="drawer-content" onClick={(e) => e.stopPropagation()} style={{ width: '700px' }}>
        
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', paddingBottom: '16px', borderBottom: '1px solid var(--border-color)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{ background: 'var(--razorpay-navy)', color: 'white', padding: '6px 10px', borderRadius: '6px', fontWeight: 800, fontSize: '0.85rem' }}>
              PANEL DEFENSE
            </div>
            <div>
              <h2 style={{ fontSize: '1.2rem', fontWeight: 700 }}>Hackathon Jury & Architecture Guide</h2>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Quick defense guide for Razorpay buildathon panel presentation</p>
            </div>
          </div>
          <button className="btn-secondary" style={{ padding: '6px' }} onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', fontSize: '0.88rem' }}>
          
          {/* Section 1: Problem & Solution */}
          <div className="card" style={{ padding: '16px', background: 'var(--bg-subtle)' }}>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--razorpay-navy)', marginBottom: '6px' }}>
              1. What problem are we solving?
            </h3>
            <p style={{ color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              Merchants lose revenue across 4 fragmented workflows (Payment Failures, Checkout Abandonments, Subscription Failures, Overdue Invoices). 
              Our Control Tower maps total revenue-at-risk, scores recoverability, ranks by <strong>Expected Recoverable Value</strong>, recommends next-best interventions via advisory AI, and enforces strict merchant policy guardrails.
            </p>
          </div>

          {/* Section 2: Deterministic vs AI Boundary */}
          <div className="card" style={{ padding: '16px' }}>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--razorpay-blue)', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Scale size={16} /> 2. Why separation between Python Math & Advisory AI?
            </h3>
            <ul style={{ listStyleType: 'none', display: 'flex', flexDirection: 'column', gap: '6px', color: 'var(--text-secondary)' }}>
              <li style={{ display: 'flex', gap: '6px' }}>
                <CheckCircle2 size={16} color="var(--success-green)" />
                <strong>Python Engine:</strong> Handles 100% of financial math, expected recovery calculations, priority queue sorting, and policy firewall checks.
              </li>
              <li style={{ display: 'flex', gap: '6px' }}>
                <CheckCircle2 size={16} color="var(--razorpay-blue)" />
                <strong>AI Reasoner:</strong> Purely advisory layer that interprets context and suggests an intervention constrained to 6 permitted actions.
              </li>
            </ul>
          </div>

          {/* Section 3: 5 Demo Scenarios */}
          <div className="card" style={{ padding: '16px' }}>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '8px' }}>
              3. 5 Hackathon Panel Demo Scenarios
            </h3>
            <ol style={{ paddingLeft: '20px', display: 'flex', flexDirection: 'column', gap: '6px', color: 'var(--text-secondary)' }}>
              <li><strong>EVT-2001 (High Recoverability):</strong> Payment failure with 85% recoverability $\rightarrow$ AI recommends RETRY_PAYMENT $\rightarrow$ Simulation succeeds.</li>
              <li><strong>EVT-2002 (Low Recoverability):</strong> Repeated failed attempts $\rightarrow$ AI recommends NO_ACTION or low priority.</li>
              <li><strong>EVT-2003 (High-Value Overdue Invoice):</strong> ₹1,25,000 invoice 45d overdue $\rightarrow$ AI recommends ESCALATE_TO_HUMAN.</li>
              <li><strong>EVT-2004 (Checkout Abandonment):</strong> ₹14,999 cart abandoned $\rightarrow$ AI recommends OFFER_APPROVED_INCENTIVE.</li>
              <li><strong>EVT-2006 (Guardrail Block):</strong> Opted-out customer $\rightarrow$ Guardrail BLOCKS action cleanly.</li>
            </ol>
          </div>

          {/* Section 4: Quick Q&A */}
          <div className="card" style={{ padding: '16px', background: 'var(--razorpay-light-blue)', border: '1px solid #BFDBFE' }}>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--razorpay-navy)', marginBottom: '6px' }}>
              4. Key Panel Q&A Pointers
            </h3>
            <p style={{ color: 'var(--text-primary)', lineHeight: 1.4 }}>
              <strong>Q: Why not prioritize purely by transaction size?</strong><br />
              <em>A: A ₹100,000 leak with 5% recoverability has only ₹5,000 expected value. A ₹10,000 leak with 85% recoverability yields ₹8,500. We prioritize expected recoverable value to maximize merchant ROI.</em>
            </p>
          </div>

        </div>

      </div>
    </div>
  );
}
