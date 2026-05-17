'use client';

import { useState, useEffect } from 'react';
import Dashboard from '@/components/Dashboard';
import { useDashboardStore } from '@/store/dashboardStore';
import { useAuthStore } from '@/store/authStore';
import LoadingScreen from '@/components/LoadingScreen';
import LoginScreen from '@/components/LoginScreen';

export default function Home() {
  const { isAuthenticated, isLoading: authLoading } = useAuthStore();
  const { fetchAllData, isLoading } = useDashboardStore();
  const [hasInitialized, setHasInitialized] = useState(false);

  useEffect(() => {
    if (isAuthenticated && !hasInitialized) {
      fetchAllData();
      setHasInitialized(true);
    }
  }, [isAuthenticated, hasInitialized, fetchAllData]);

  if (authLoading) {
    return <LoadingScreen />;
  }

  if (!isAuthenticated) {
    return <LoginScreen />;
  }

  return (
    <div className="min-h-screen bg-dark-bg">
      <Dashboard isLoading={isLoading} />
    </div>
  );
}
