'use client';

import { useDashboardStore } from '@/store/dashboardStore';
import { getSignalColor, getSignalBgColor, formatConfidence } from '@/utils/styling';
import SkeletonLoader from '../SkeletonLoader';

interface DeepLearningPanelProps {
  isLoading: boolean;
}

export default function DeepLearningPanel({ isLoading }: DeepLearningPanelProps) {
  const { deepLearning } = useDashboardStore();

  if (isLoading) {
    return (
      <div className="glass-lg rounded-2xl p-6 animate-slide-up">
        <SkeletonLoader height="h-64" />
      </div>
    );
  }

  if (!deepLearning) {
    return (
      <div className="glass-lg rounded-2xl p-6 text-center">
        <p className="text-gray-400 text-sm">No deep learning data</p>
      </div>
    );
  }

  return (
    <div className={`glass-lg rounded-2xl p-6 border ${getSignalBgColor(deepLearning.prediction)} animate-slide-up`}>
      {/* Header */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-white mb-2">Deep Learning Model</h3>
        <p className="text-xs text-gray-400">{deepLearning.model_name}</p>
      </div>

      {/* Main Prediction */}
      <div className="text-center mb-6">
        <div className={`text-4xl font-bold mb-4 ${getSignalColor(deepLearning.prediction)}`}>
          {deepLearning.prediction}
        </div>

        {/* Confidence */}
        <div>
          <p className="text-gray-400 text-xs mb-2">Model Confidence</p>
          <div className="relative h-2 bg-dark-panel/50 rounded-full overflow-hidden mb-2">
            <div
              className="h-full bg-gradient-to-r from-neon-green to-neon-blue"
              style={{
                width: `${deepLearning.confidence * 100}%`,
              }}
            />
          </div>
          <p className="text-sm font-semibold text-neon-green">
            {formatConfidence(deepLearning.confidence)}
          </p>
        </div>
      </div>

      {/* Explanation */}
      {deepLearning.explanation && (
        <div className="mt-6 p-3 rounded bg-dark-panel/30 border border-dark-border">
          <p className="text-xs text-gray-400 mb-2">Model Explanation</p>
          <p className="text-sm text-gray-300 leading-relaxed">
            {deepLearning.explanation}
          </p>
        </div>
      )}

      {/* Timestamp */}
      <p className="text-xs text-gray-500 text-center mt-4">
        {new Date(deepLearning.timestamp).toLocaleTimeString()}
      </p>
    </div>
  );
}
