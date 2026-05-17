import { create } from 'zustand';
import { DashboardState } from '@/types';
import { apiClient } from '@/services/apiClient';

interface DashboardStoreState extends DashboardState {
  fetchAllData: () => Promise<void>;
  setError: (error: string | null) => void;
  reset: () => void;
}

export const useDashboardStore = create<DashboardStoreState>((set) => ({
  finalSignal: null,
  correlation: null,
  deepLearning: null,
  mood: null,
  isLoading: false,
  error: null,
  lastUpdated: null,

  fetchAllData: async () => {
    set({ isLoading: true, error: null });
    try {
      const [finalSignal, correlation, deepLearning, mood] = await Promise.all([
        apiClient.getFinalSignal(),
        apiClient.getCorrelation(),
        apiClient.getDeepLearning(),
        apiClient.getMood(),
      ]);

      set({
        finalSignal,
        correlation,
        deepLearning,
        mood,
        isLoading: false,
        lastUpdated: new Date().toISOString(),
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch dashboard data';
      set({
        error: errorMessage,
        isLoading: false,
      });
      console.error('Dashboard data fetch error:', error);
    }
  },

  setError: (error) => set({ error }),

  reset: () => {
    set({
      finalSignal: null,
      correlation: null,
      deepLearning: null,
      mood: null,
      isLoading: false,
      error: null,
      lastUpdated: null,
    });
  },
}));
