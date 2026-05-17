'use client';

import { useEffect } from 'react';
import { useAuthStore } from '@/store/authStore';

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { setAuthenticated, setLoading, setUser } = useAuthStore();

  useEffect(() => {
    // Check if user is already authenticated from localStorage
    const storedUser = localStorage.getItem('auth_user');
    const storedToken = localStorage.getItem('auth_token');

    if (storedUser && storedToken) {
      try {
        const user = JSON.parse(storedUser);
        setUser(user);
        setAuthenticated(true);
      } catch (error) {
        console.error('Failed to parse stored auth:', error);
        localStorage.removeItem('auth_user');
        localStorage.removeItem('auth_token');
      }
    }

    setLoading(false);
  }, [setAuthenticated, setLoading, setUser]);

  return <>{children}</>;
}
