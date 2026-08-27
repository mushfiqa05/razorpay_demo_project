import React from 'react';
import { 
  LayoutDashboard, 
  ListFilter, 
  Activity, 
  History, 
  Settings, 
  ShieldCheck, 
  Building2 
} from 'lucide-react';

export default function Sidebar({ currentPage, setCurrentPage, merchantName }) {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'opportunities', label: 'Opportunities', icon: ListFilter },
    { id: 'activity', label: 'Recovery Activity', icon: Activity },
    { id: 'audit', label: 'Audit Trail', icon: History },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="sidebar">
      <div>
        {/* Logo / Brand Header */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '32px', padding: '0 8px' }}>
          <div style={{ 
            width: '38px', 
            height: '38px', 
            borderRadius: '8px', 
            background: 'var(--razorpay-navy)', 
            color: 'white', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            fontWeight: 800,
            fontSize: '1.2rem'
          }}>
            R
          </div>
          <div>
            <h1 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)', lineHeight: 1.2 }}>
              Revenue Recovery
            </h1>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 500 }}>
              Control Tower
            </span>
          </div>
        </div>

        {/* Navigation Menu */}
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setCurrentPage(item.id)}
                style={{
                  width: '100%',
                  justifyContent: 'flex-start',
                  padding: '10px 12px',
                  background: isActive ? 'var(--razorpay-light-blue)' : 'transparent',
                  color: isActive ? 'var(--razorpay-blue)' : 'var(--text-secondary)',
                  border: 'none',
                  borderRadius: '6px',
                  fontWeight: isActive ? 600 : 500,
                  fontSize: '0.875rem',
                }}
              >
                <Icon size={18} color={isActive ? 'var(--razorpay-blue)' : '#64748B'} />
                {item.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Footer Merchant & Sandbox Indicator */}
      <div style={{ 
        padding: '16px', 
        background: 'var(--bg-subtle)', 
        borderRadius: '8px', 
        border: '1px solid var(--border-color)' 
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
          <Building2 size={16} color="var(--text-secondary)" />
          <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>
            {merchantName || 'UrbanKart Retail'}
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <ShieldCheck size={14} color="var(--success-green)" />
          <span style={{ fontSize: '0.75rem', color: 'var(--success-green)', fontWeight: 600 }}>
            SANDBOX ENVIRONMENT
          </span>
        </div>
      </div>
    </aside>
  );
}
