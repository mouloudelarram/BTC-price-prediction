'use client';

import { FiRefreshCw } from 'react-icons/fi';
import { cn } from '@/utils/styling';

interface RefreshButtonProps {
  onClick: () => void;
  isLoading?: boolean;
}

export default function RefreshButton({ onClick, isLoading = false }: RefreshButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={isLoading}
      className={cn(
        'px-4 py-2 rounded-lg border border-neon-blue/30 bg-neon-blue/10 text-neon-blue',
        'hover:bg-neon-blue/20 hover:shadow-glow-blue transition-all',
        'flex items-center gap-2 text-sm font-medium',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        isLoading && 'animate-spin'
      )}
    >
      <FiRefreshCw size={16} className={isLoading ? 'animate-spin' : ''} />
      {isLoading ? 'Updating...' : 'Refresh'}
    </button>
  );
}
