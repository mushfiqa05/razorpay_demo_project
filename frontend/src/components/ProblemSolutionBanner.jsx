import React, { useState } from 'react';
import { ShieldCheck, Zap, ArrowRight, AlertTriangle, Cpu, CheckCircle2, ChevronRight } from 'lucide-react';

export default function ProblemSolutionBanner() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div style={{ 
      background: 'linear-gradient(135deg, #0F172A 0%, #1E293B 100%)', 
      borderRadius: '12px', 
      padding: collapsed ? '14px 20px' : '20px 24px', 
      color: 'white',
      boxShadow: '0 4px 12px rgba(15, 23, 42, 0.15)',
      border: '1px solid #334155',
      marginBottom: '8px',
      transition: 'all 0.2s ease'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ 
            background: 'rgba(12, 108, 242, 0.2)', 
            border: '1px solid #0C6CF2', 
            borderRadius: '8px', 
            padding: '6px 10px', 
            display: 'flex', 
            alignItems: 'center', 
            gap: '6px' 
          }}>
            <ShieldCheck size={18} color="#38BDF8" />
            <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#38BDF8', letterSpacing: '0.04em' }}>
              HOW IT WORKS
            </span>
          </div>
          <h2 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#F8FAFC' }}>
            Autonomous AI Revenue Recovery Engine for Razorpay Merchants
          </h2>
        </div>

        <button 
          onClick={() => setCollapsed(!collapsed)}
          style={{ 
            background: 'rgba(255,255,255,0.08)', 
            border: '1px solid rgba(255,255,255,0.15)', 
            color: '#94A3B8', 
            fontSize: '0.78rem',
            padding: '4px 10px'
          }}
        >
          {collapsed ? 'Show Architecture Flow' : 'Hide Flow'}
        </button>
      </div>

      {!collapsed && (
        <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
            gap: '12px', 
            alignItems: 'center' 
          }}>
            
            {/* Step 1: Fragmented Leaks */}
            <div style={{ background: 'rgba(255,255,255,0.05)', padding: '12px 14px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.08)' }}>
              <div style={{ fontSize: '0.72rem', color: '#FCA5A5', fontWeight: 700, marginBottom: '4px', textTransform: 'uppercase' }}>
                1. Fragmented Leaks
              </div>
              <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#F1F5F9' }}>
                Payment, Cart, SaaS & Invoices
              </div>
              <div style={{ fontSize: '0.75rem', color: '#94A3B8', marginTop: '2px' }}>
                Maps ₹ risk across 4 workflows
              </div>
            </div>

            <ChevronRight size={18} color="#64748B" style={{ display: 'none', minWidth: '18px' }} />

            {/* Step 2: Expected Value Scoring */}
            <div style={{ background: 'rgba(255,255,255,0.05)', padding: '12px 14px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.08)' }}>
              <div style={{ fontSize: '0.72rem', color: '#38BDF8', fontWeight: 700, marginBottom: '4px', textTransform: 'uppercase' }}>
                2. Expected Value Math
              </div>
              <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#F1F5F9' }}>
                Risk × Recoverability %
              </div>
              <div style={{ fontSize: '0.75rem', color: '#94A3B8', marginTop: '2px' }}>
                Deterministic priority ranking
              </div>
            </div>

            {/* Step 3: Advisory AI */}
            <div style={{ background: 'rgba(255,255,255,0.05)', padding: '12px 14px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.08)' }}>
              <div style={{ fontSize: '0.72rem', color: '#C084FC', fontWeight: 700, marginBottom: '4px', textTransform: 'uppercase' }}>
                3. Advisory AI Reasoner
              </div>
              <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#F1F5F9' }}>
                Next-Best Intervention
              </div>
              <div style={{ fontSize: '0.75rem', color: '#94A3B8', marginTop: '2px' }}>
                Constrained to 6 allowed actions
              </div>
            </div>

            {/* Step 4: Guardrail Firewall */}
            <div style={{ background: 'rgba(255,255,255,0.05)', padding: '12px 14px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.08)' }}>
              <div style={{ fontSize: '0.72rem', color: '#4ADE80', fontWeight: 700, marginBottom: '4px', textTransform: 'uppercase' }}>
                4. Policy Guardrail Firewall
              </div>
              <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#F1F5F9' }}>
                7 Merchant Safety Rules
              </div>
              <div style={{ fontSize: '0.75rem', color: '#94A3B8', marginTop: '2px' }}>
                Blocks unpermitted actions
              </div>
            </div>

          </div>
        </div>
      )}
    </div>
  );
}
