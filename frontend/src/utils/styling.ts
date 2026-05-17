import clsx, { ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Merge Tailwind CSS classes with clsx support
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format confidence percentage
 */
export function formatConfidence(confidence: number): string {
  return `${Math.round(confidence * 100)}%`;
}

/**
 * Get signal color classes
 */
export function getSignalColor(signal: string): string {
  switch (signal.toUpperCase()) {
    case 'BUY':
      return 'text-neon-green';
    case 'SELL':
      return 'text-neon-red';
    case 'HOLD':
    case 'NEUTRAL':
      return 'text-neon-blue';
    default:
      return 'text-gray-400';
  }
}

/**
 * Get signal background color
 */
export function getSignalBgColor(signal: string): string {
  switch (signal.toUpperCase()) {
    case 'BUY':
      return 'bg-neon-green/10 border-neon-green/30';
    case 'SELL':
      return 'bg-neon-red/10 border-neon-red/30';
    case 'HOLD':
    case 'NEUTRAL':
      return 'bg-neon-blue/10 border-neon-blue/30';
    default:
      return 'bg-dark-panel/30 border-dark-border';
  }
}

/**
 * Get sentiment color
 */
export function getSentimentColor(sentiment: string): string {
  switch (sentiment.toUpperCase()) {
    case 'POSITIVE':
    case 'BULLISH':
      return 'text-neon-green';
    case 'NEGATIVE':
    case 'BEARISH':
      return 'text-neon-red';
    default:
      return 'text-neon-blue';
  }
}

/**
 * Format timestamp
 */
export function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp);
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Format correlation value
 */
export function formatCorrelation(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}
