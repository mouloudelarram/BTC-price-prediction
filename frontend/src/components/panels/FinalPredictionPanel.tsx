'use client';

import { useDashboardStore } from '@/store/dashboardStore';
import { getSignalColor, getSignalBgColor, formatConfidence, formatTimestamp } from '@/utils/styling';
import SkeletonLoader from '../SkeletonLoader';

interface FinalPredictionPanelProps {
  isLoading: boolean;
}

export default function FinalPredictionPanel({ isLoading }: FinalPredictionPanelProps) {
  const { finalSignal } = useDashboardStore();

  if (isLoading) {
    return (
      <div className="glass-lg rounded-2xl p-8 animate-slide-up">
        <SkeletonLoader height="h-48" />
      </div>
    );
  }

  if (!finalSignal) {
    return (
      <div className="glass-lg rounded-2xl p-8 text-center">
        <p className="text-gray-400">No signal data available</p>
      </div>
    );
  }

  return (
    <div className={`glass-lg rounded-2xl p-8 border-2 ${getSignalBgColor(finalSignal.signal)} animate-slide-up`}>
      <div className="text-center">
        <p className="text-gray-400 text-sm uppercase tracking-widest mb-4">Final Signal</p>

        {/* Main Signal */}
        <div className={`text-7xl font-bold mb-6 ${getSignalColor(finalSignal.signal)}`}>
          {finalSignal.signal}
        </div>

        {/* Confidence Score */}
        <div className="space-y-4 mb-6">
          <div>
            <p className="text-gray-400 text-sm mb-2">Confidence Score</p>
            <div className="relative h-2 bg-dark-panel/50 rounded-full overflow-hidden">
              <div
                className={`h-full bg-gradient-to-r ${
                  finalSignal.signal === 'BUY'
                    ? 'from-neon-green to-neon-green/50'
                    : 'from-neon-red to-neon-red/50'
                }`}
                style={{
                  width: `${finalSignal.confidence * 100}%`,
                }}
              />
            </div>
            <p className="text-neon-blue font-semibold mt-2">
              {formatConfidence(finalSignal.confidence)}
            </p>
          </div>
        </div>

        {/* Timestamp */}
        <p className="text-gray-500 text-xs">
          {formatTimestamp(finalSignal.timestamp)}
        </p>
      </div>

      {/* Bottom accent line */}
      <div className={`mt-6 h-1 rounded-full bg-gradient-to-r ${
        finalSignal.signal === 'BUY'
          ? 'from-neon-green/0 via-neon-green to-neon-green/0'
          : 'from-neon-red/0 via-neon-red to-neon-red/0'
      }`} />
    </div>
  );
}
