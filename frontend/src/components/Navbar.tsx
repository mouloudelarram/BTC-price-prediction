'use client';

import Link from 'next/link';
import { useAuthStore } from '@/store/authStore';
import { useHealthCheck } from '@/hooks/useHealthCheck';
import { FiLogOut, FiMenu } from 'react-icons/fi';
import { useState } from 'react';

export default function Navbar() {
  const { user, logout } = useAuthStore();
  const { isHealthy } = useHealthCheck();
  const [menuOpen, setMenuOpen] = useState(false);

  const navLinks = [
    { label: 'Dashboard', href: '/' },
    { label: 'Signals', href: '/signals' },
    { label: 'Correlation', href: '/correlation' },
    { label: 'Mood', href: '/mood' },
    { label: 'Deep Learning', href: '/dl' },
  ];

  return (
    <nav className="glass-lg sticky top-0 z-50 border-b">
      <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
        {/* Logo */}
        <Link href="/" className="text-2xl font-bold text-neon-blue">
          BNMP
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center gap-8">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="text-sm text-gray-300 hover:text-neon-blue transition-colors"
            >
              {link.label}
            </Link>
          ))}
        </div>

        {/* Right section */}
        <div className="flex items-center gap-4">
          {/* Health indicator */}
          <div className="flex items-center gap-2">
            <div
              className={`w-2 h-2 rounded-full ${
                isHealthy ? 'bg-neon-green glow-green' : 'bg-neon-red glow-red'
              }`}
            />
            <span className="text-xs text-gray-400">{isHealthy ? 'Connected' : 'Offline'}</span>
          </div>

          {/* User info */}
          {user && (
            <div className="hidden md:flex items-center gap-2">
              {user.picture && (
                <img
                  src={user.picture}
                  alt={user.name}
                  className="w-8 h-8 rounded-full border border-neon-blue/30"
                />
              )}
              <span className="text-sm text-gray-300">{user.email}</span>
            </div>
          )}

          {/* Logout button */}
          <button
            onClick={logout}
            className="flex items-center gap-2 px-4 py-2 rounded bg-neon-red/10 border border-neon-red/30 text-neon-red hover:bg-neon-red/20 transition-colors"
          >
            <FiLogOut size={16} />
            <span className="hidden md:inline text-sm">Logout</span>
          </button>

          {/* Mobile menu toggle */}
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="md:hidden text-neon-blue"
          >
            <FiMenu size={24} />
          </button>
        </div>
      </div>

      {/* Mobile Navigation */}
      {menuOpen && (
        <div className="md:hidden border-t border-dark-border p-4 space-y-2">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="block px-4 py-2 text-sm text-gray-300 hover:text-neon-blue hover:bg-dark-panel/30 rounded transition-colors"
              onClick={() => setMenuOpen(false)}
            >
              {link.label}
            </Link>
          ))}
        </div>
      )}
    </nav>
  );
}
