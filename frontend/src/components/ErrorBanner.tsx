'use client';

import { FiAlertCircle, FiX } from 'react-icons/fi';
import { useState } from 'react';

interface ErrorBannerProps {
  message: string;
}

export default function ErrorBanner({ message }: ErrorBannerProps) {
  const [isVisible, setIsVisible] = useState(true);

  if (!isVisible) return null;

  return (
    <div className="bg-neon-red/10 border-t border-b border-neon-red/30 px-4 py-3 flex items-center justify-between animate-slide-up">
      <div className="flex items-center gap-3">
        <FiAlertCircle className="text-neon-red" size={20} />
        <p className="text-neon-red text-sm">{message}</p>
      </div>
      <button
        onClick={() => setIsVisible(false)}
        className="text-neon-red/70 hover:text-neon-red transition-colors"
      >
        <FiX size={20} />
      </button>
    </div>
  );
}
