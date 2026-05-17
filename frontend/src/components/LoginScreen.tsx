'use client';

import { useGoogleLogin } from '@react-oauth/google';
import { useAuthStore } from '@/store/authStore';
import { FiLogIn } from 'react-icons/fi';

export default function LoginScreen() {
  const { setUser, setAuthenticated } = useAuthStore();

  const login = useGoogleLogin({
    onSuccess: async (codeResponse) => {
      try {
        // Fetch user info from Google token
        const response = await fetch('https://www.googleapis.com/oauth2/v1/userinfo', {
          headers: {
            Authorization: `Bearer ${codeResponse.access_token}`,
          },
        });

        const userInfo = await response.json();

        // Store auth data
        const user = {
          id: userInfo.id,
          email: userInfo.email,
          name: userInfo.name,
          picture: userInfo.picture,
        };

        localStorage.setItem('auth_user', JSON.stringify(user));
        localStorage.setItem('auth_token', codeResponse.access_token);

        setUser(user);
        setAuthenticated(true);
      } catch (error) {
        console.error('Login error:', error);
      }
    },
    flow: 'implicit',
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark-bg to-dark-panel flex items-center justify-center px-4">
      <div className="glass-lg rounded-2xl p-12 max-w-md w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-neon-blue mb-2">BNMP</h1>
          <p className="text-gray-400">BTC Next Move Prediction</p>
        </div>

        {/* Description */}
        <div className="mb-8">
          <p className="text-center text-gray-300 mb-4">
            Welcome to the production-grade financial dashboard. Sign in with your Google account to access real-time AI predictions for Bitcoin.
          </p>
          <div className="space-y-2 text-sm text-gray-400">
            <p>✓ Real-time AI predictions</p>
            <p>✓ Multi-model correlation engine</p>
            <p>✓ Social mood analysis</p>
            <p>✓ Institutional-grade UI</p>
          </div>
        </div>

        {/* Login Button */}
        <button
          onClick={() => login()}
          className="w-full py-3 px-4 rounded-lg bg-gradient-to-r from-neon-blue to-neon-green text-dark-bg font-semibold flex items-center justify-center gap-2 hover:shadow-glow-blue transition-all hover:scale-105"
        >
          <FiLogIn size={20} />
          Sign in with Google
        </button>

        {/* Footer */}
        <p className="text-center text-xs text-gray-500 mt-8">
          Secure authentication via Google OAuth
        </p>
      </div>
    </div>
  );
}
