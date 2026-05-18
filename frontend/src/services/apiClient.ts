import axios, { AxiosInstance } from 'axios';
import {
  FinalSignalResponse,
  CorrelationResponse,
  DeepLearningResponse,
  MoodResponse,
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor for auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );
  }

  // Final Signal API
  async getFinalSignal(): Promise<FinalSignalResponse> {
    try {
      const response = await this.client.get('/api/v1/correlation/signal');
      console.log('Final Signal Response: ', response.data);
      return response.data;
    } catch (error) {
      console.error('Error fetching final signal:', error);
      throw error;
    }
  }

  // Correlation Engine API
  async getCorrelation(): Promise<CorrelationResponse> {
    try {
      const response = await this.client.get('/api/v1/correlation/summary');
      console.log('Correlation Response: ', response.data);
      return response.data;
    } catch (error) {
      console.error('Error fetching correlation data:', error);
      throw error;
    }
  }

  // Deep Learning Model API
  async getDeepLearning(): Promise<DeepLearningResponse> {
    try {
      const response = await this.client.get('/api/v1/correlation/signal');
      return response.data;
    } catch (error) {
      console.error('Error fetching deep learning prediction:', error);
      throw error;
    }
  }

  // Mood Engine API
  async getMood(): Promise<MoodResponse> {
    try {
      const response = await this.client.get('/api/v1/correlation/signal');
      return response.data;
    } catch (error) {
      console.error('Error fetching mood data:', error);
      throw error;
    }
  }

  // Health check
  async healthCheck(): Promise<boolean> {
    try {
      const response = await this.client.get('/health', { timeout: 5000 });
      return response.status === 200;
    } catch {
      return false;
    }
  }
}

export const apiClient = new APIClient();
