'use client';

import { useDashboardStore } from '@/store/dashboardStore';
import { getSentimentColor, getSignalBgColor } from '@/utils/styling';
import SkeletonLoader from '../SkeletonLoader';
import { FiTrendingUp, FiTrendingDown } from 'react-icons/fi';

interface MoodPanelProps {
  isLoading: boolean;
}

export default function MoodPanel({ isLoading }: MoodPanelProps) {
  const { mood } = useDashboardStore();

  if (isLoading) {
    return (
      <div className="glass-lg rounded-2xl p-6 animate-slide-up">
        <SkeletonLoader height="h-64" />
      </div>
    );
  }

  if (!mood) {
    return (
      <div className="glass-lg rounded-2xl p-6 text-center">
        <p className="text-gray-400 text-sm">No mood data</p>
      </div>
    );
  }

  const isBullish = mood.trend === 'BULLISH';
  const trendColor = isBullish ? 'text-neon-green' : 'text-neon-red';

  return (
    <div className="glass-lg rounded-2xl p-6 animate-slide-up">
      {/* Header */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-white mb-2">Social Mood Engine</h3>
        <p className={`text-xs ${getSentimentColor(mood.current.classification)}`}>
          {mood.current.classification}
        </p>
      </div>

      {/* Sentiment Score */}
      <div className="text-center mb-6">
        {/* Gauge */}
        <div className="mb-4">
          <div className="relative w-32 h-32 mx-auto rounded-full bg-gradient-to-br from-dark-panel/50 to-dark-panel/20 border-2 border-dark-border flex items-center justify-center">
            <div className="text-center">
              <div className={`text-3xl font-bold ${getSentimentColor(mood.current.classification)}`}>
                {(mood.current.sentiment_score * 100).toFixed(0)}
              </div>
              <p className="text-xs text-gray-400">Score</p>
            </div>
          </div>
        </div>

        {/* Trend Indicator */}
        <div className={`flex items-center justify-center gap-2 mb-4 ${trendColor}`}>
          {isBullish ? (
            <FiTrendingUp size={20} />
          ) : (
            <FiTrendingDown size={20} />
          )}
          <span className="font-semibold">{mood.trend}</span>
        </div>
      </div>

      {/* Headlines */}
      {mood.headline_preview && mood.headline_preview.length > 0 && (
        <div className="mt-6 pt-6 border-t border-dark-border">
          <p className="text-xs text-gray-400 mb-3">Recent Headlines</p>
          <div className="space-y-2">
            {mood.headline_preview.slice(0, 2).map((headline, idx) => (
              <p
                key={idx}
                className="text-xs text-gray-300 leading-relaxed line-clamp-2 hover:text-gray-200 transition-colors"
              >
                {headline}
              </p>
            ))}
          </div>
        </div>
      )}

      {/* Timestamp */}
      <p className="text-xs text-gray-500 text-center mt-4">
        {new Date(mood.timestamp).toLocaleTimeString()}
      </p>
    </div>
  );
}
