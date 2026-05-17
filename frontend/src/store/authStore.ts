import { create } from 'zustand';
import { AuthState, User } from '@/types';

interface AuthStoreState extends AuthState {
  setUser: (user: User | null) => void;
  setAuthenticated: (isAuthenticated: boolean) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthStoreState>((set) => {
  // Initialize from localStorage if available
  if (typeof window !== 'undefined') {
    const storedAuth = localStorage.getItem('auth_user');
    const storedToken = localStorage.getItem('auth_token');
    if (storedAuth && storedToken) {
      set({
        user: JSON.parse(storedAuth),
        isAuthenticated: true,
      });
    }
  }

  return {
    user: null,
    isAuthenticated: false,
    isLoading: true,
    error: null,

    setUser: (user) => set({ user }),
    setAuthenticated: (isAuthenticated) => set({ isAuthenticated }),
    setLoading: (isLoading) => set({ isLoading }),
    setError: (error) => set({ error }),

    logout: () => {
      localStorage.removeItem('auth_user');
      localStorage.removeItem('auth_token');
      set({
        user: null,
        isAuthenticated: false,
        error: null,
      });
    },
  };
});
