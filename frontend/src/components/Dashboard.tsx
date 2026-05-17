'use client';

import { useEffect } from 'react';
import { useDashboardStore } from '@/store/dashboardStore';
import FinalPredictionPanel from './panels/FinalPredictionPanel';
import CorrelationPanel from './panels/CorrelationPanel';
import DeepLearningPanel from './panels/DeepLearningPanel';
import MoodPanel from './panels/MoodPanel';
import ErrorBanner from './ErrorBanner';
import RefreshButton from './RefreshButton';

interface DashboardProps {
  isLoading: boolean;
}

export default function Dashboard({ isLoading }: DashboardProps) {
  const { fetchAllData, error, lastUpdated } = useDashboardStore();

  useEffect(() => {
    const interval = setInterval(() => {
      fetchAllData();
    }, Number(process.env.NEXT_PUBLIC_API_POLLING_INTERVAL) || 60000);

    return () => clearInterval(interval);
  }, [fetchAllData]);

  return (
    <div className="min-h-screen bg-dark-bg">
      {/* Header */}
      <div className="bg-dark-panel/30 border-b border-dark-border sticky top-0 z-30 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-white mb-1">Dashboard</h1>
              <p className="text-sm text-gray-400">
                {lastUpdated && `Last updated: ${new Date(lastUpdated).toLocaleTimeString()}`}
              </p>
            </div>
            <RefreshButton onClick={() => fetchAllData()} isLoading={isLoading} />
          </div>
        </div>
      </div>

      {/* Error Banner */}
      {error && <ErrorBanner message={error} />}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
        {/* Panel 1: Final Prediction (Hero) */}
        <FinalPredictionPanel isLoading={isLoading} />

        {/* Panels 2-4: Grid layout */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <CorrelationPanel isLoading={isLoading} />
          <DeepLearningPanel isLoading={isLoading} />
          <MoodPanel isLoading={isLoading} />
        </div>
      </div>
    </div>
  );
}
