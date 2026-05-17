// API Response Types
export interface FinalSignalResponse {
  signal: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  timestamp: string;
}

export interface CorrelationData {
  index_name: string;
  correlation_value: number;
  lag_value?: number;
}

export interface CorrelationResponse {
  summary: {
    top_correlations: CorrelationData[];
    average_correlation: number;
  };
  signal: 'BUY' | 'SELL' | 'NEUTRAL';
}

export interface DeepLearningResponse {
  prediction: 'BUY' | 'SELL';
  confidence: number;
  model_name: string;
  timestamp: string;
  explanation?: string;
}

export interface MoodData {
  sentiment_score: number;
  classification: 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL';
  source?: string;
}

export interface MoodResponse {
  current: MoodData;
  trend: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
  headline_preview?: string[];
  timestamp: string;
}

export interface DashboardState {
  finalSignal: FinalSignalResponse | null;
  correlation: CorrelationResponse | null;
  deepLearning: DeepLearningResponse | null;
  mood: MoodResponse | null;
  isLoading: boolean;
  error: string | null;
  lastUpdated: string | null;
}

export interface User {
  id: string;
  email: string;
  name: string;
  picture?: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}
