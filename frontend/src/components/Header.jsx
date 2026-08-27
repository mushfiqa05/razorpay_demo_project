import React, { useState } from 'react';
import { RefreshCw, ShieldAlert, Building, BookOpen } from 'lucide-react';
import JuryGuideModal from './JuryGuideModal';

export default function Header({ 
  title, 
  subtitle, 
  merchants, 
  selectedMerchantId, 
  setSelectedMerchantId, 
  onRefresh, 
  isRefreshing 
}) {
  const [showJuryGuide, setShowJuryGuide] = useState(false);

  return (
    <>
      <header className="header">
        <div>
          <h1 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)' }}>
            {title}
          </h1>
          {subtitle && (
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
              {subtitle}
            </p>
          )}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          {/* Merchant Dropdown Selector */}
          {merchants && merchants.length > 0 && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Building size={16} color="var(--text-secondary)" />
              <select
                value={selectedMerchantId}
                onChange={(e) => setSelectedMerchantId(e.target.value)}
                style={{ fontWeight: 600, padding: '6px 12px' }}
              >
                {merchants.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.name} ({m.industry.split('&')[0]})
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Jury Pitch Guide Button */}
          <button 
            className="btn-primary"
            onClick={() => setShowJuryGuide(true)}
            style={{ padding: '6px 12px', fontSize: '0.8rem', background: 'var(--razorpay-blue)', border: 'none' }}
          >
            <BookOpen size={14} /> Jury Pitch Guide
          </button>

          {/* Sandbox Environment Tag */}
          <span className="badge badge-neutral" style={{ padding: '6px 12px' }}>
            <ShieldAlert size={14} color="var(--warning-amber)" />
            DEMO MODE
          </span>

          {/* Refresh Button */}
          <button 
            className="btn-secondary" 
            onClick={onRefresh}
            disabled={isRefreshing}
            style={{ padding: '6px 14px' }}
          >
            <RefreshCw size={14} className={isRefreshing ? 'spin' : ''} />
            Refresh Data
          </button>
        </div>
      </header>

      {/* Jury Guide Modal Overlay */}
      {showJuryGuide && (
        <JuryGuideModal onClose={() => setShowJuryGuide(false)} />
      )}
    </>
  );
}
