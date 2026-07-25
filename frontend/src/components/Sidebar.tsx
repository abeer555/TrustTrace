'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  ShieldCheck,
  LayoutDashboard,
  BellRing,
  Users,
  Activity,
  Zap,
} from 'lucide-react';

const navItems = [
  { href: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { href: '/alerts', icon: BellRing, label: 'Alert Queue' },
  { href: '/entities', icon: Users, label: 'Entities' },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <nav className="sidebar">
      {/* Logo */}
      <div className="sidebar-logo">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div
            style={{
              width: 36,
              height: 36,
              borderRadius: 8,
              background: 'linear-gradient(135deg, #0891b2, #3b82f6)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 16px rgba(0,212,255,0.4)',
            }}
          >
            <ShieldCheck size={20} color="#fff" />
          </div>
          <div>
            <div style={{ fontSize: 16, fontWeight: 800, color: '#e2e8f0', letterSpacing: '-0.3px' }}>
              TrustTrace
            </div>
            <div style={{ fontSize: 10, color: '#00d4ff', fontWeight: 600, letterSpacing: '1.5px', textTransform: 'uppercase' }}>
              Threat Intel
            </div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <div style={{ padding: '8px 0' }}>
        <div style={{ fontSize: 10, color: '#475569', fontWeight: 600, letterSpacing: '1.5px', textTransform: 'uppercase', padding: '8px 20px 4px' }}>
          Navigation
        </div>
        {navItems.map(({ href, icon: Icon, label }) => {
          const active = pathname === href || (href !== '/' && pathname.startsWith(href));
          return (
            <Link key={href} href={href} className={`sidebar-nav-item ${active ? 'active' : ''}`}>
              <Icon size={16} />
              {label}
            </Link>
          );
        })}
      </div>

      {/* Status indicator */}
      <div style={{ marginTop: 'auto', padding: '0 20px 8px' }}>
        <div
          style={{
            background: 'rgba(16,185,129,0.08)',
            border: '1px solid rgba(16,185,129,0.25)',
            borderRadius: 8,
            padding: '10px 12px',
            display: 'flex',
            alignItems: 'center',
            gap: 8,
          }}
        >
          <div
            style={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              background: '#10b981',
              boxShadow: '0 0 8px #10b981',
              animation: 'pulse-glow 2s infinite',
            }}
          />
          <div>
            <div style={{ fontSize: 11, fontWeight: 600, color: '#6ee7b7' }}>System Online</div>
            <div style={{ fontSize: 10, color: '#475569' }}>Monitoring active</div>
          </div>
        </div>
      </div>
    </nav>
  );
}
