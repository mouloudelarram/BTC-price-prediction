'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/services/apiClient';

export function useHealthCheck() {
  const [isHealthy, setIsHealthy] = useState(true);

  useEffect(() => {
    const checkHealth = async () => {
      const healthy = await apiClient.healthCheck();
      setIsHealthy(healthy);
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000);

    return () => clearInterval(interval);
  }, []);

  return { isHealthy };
}
