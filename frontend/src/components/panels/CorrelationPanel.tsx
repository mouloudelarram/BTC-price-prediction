'use client';

import { useDashboardStore } from '@/store/dashboardStore';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { formatCorrelation, getSignalColor } from '@/utils/styling';
import SkeletonLoader from '../SkeletonLoader';

interface CorrelationPanelProps {
  isLoading: boolean;
}

export default function CorrelationPanel({ isLoading }: CorrelationPanelProps) {
  const { correlation } = useDashboardStore();

  if (isLoading) {
    return (
      <div className="glass-lg rounded-2xl p-6 animate-slide-up">
        <SkeletonLoader height="h-64" />
      </div>
    );
  }

  if (!correlation) {
    return (
      <div className="glass-lg rounded-2xl p-6 text-center">
        <p className="text-gray-400 text-sm">No correlation data</p>
      </div>
    );
  }

  const chartData = correlation.summary.top_correlations.map((item) => ({
    name: item.index_name.substring(0, 8),
    value: item.correlation_value,
  }));

  return (
    <div className="glass-lg rounded-2xl p-6 animate-slide-up">
      {/* Header */}
      <div className="flex justify-between items-start mb-6">
        <div>
          <h3 className="text-lg font-semibold text-white mb-1">Correlation Engine</h3>
          <p className={`text-sm ${getSignalColor(correlation.signal)}`}>
            Signal: {correlation.signal}
          </p>
        </div>
        <span className="text-xs bg-dark-panel/50 px-3 py-1 rounded-full text-gray-400">
          Avg: {formatCorrelation(correlation.summary.average_correlation)}
        </span>
      </div>

      {/* Chart */}
      <div className="h-64 -mx-2">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 20 }}>
            <XAxis
              dataKey="name"
              stroke="#666"
              style={{ fontSize: '12px' }}
            />
            <YAxis stroke="#666" style={{ fontSize: '12px' }} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1a1f3a',
                border: '1px solid #2d3561',
                borderRadius: '8px',
              }}
              formatter={(value) => formatCorrelation(value as number)}
            />
            <Bar dataKey="value" fill="#00d4ff" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Top correlations list */}
      <div className="mt-6 space-y-2">
        {correlation.summary.top_correlations.slice(0, 3).map((item, idx) => (
          <div key={idx} className="flex justify-between items-center p-2 rounded bg-dark-panel/30">
            <span className="text-sm text-gray-300">{item.index_name}</span>
            <span className="text-sm font-semibold text-neon-blue">
              {formatCorrelation(item.correlation_value)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
