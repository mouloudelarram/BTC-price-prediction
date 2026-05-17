import type { Metadata } from 'next';
import { GoogleOAuthProvider } from '@react-oauth/google';
import './globals.css';
import Navbar from '@/components/Navbar';
import { AuthProvider } from '@/components/AuthProvider';

export const metadata: Metadata = {
  title: 'BNMP Dashboard - BTC Prediction',
  description: 'Production-grade financial dashboard for Bitcoin next move prediction',
  viewport: 'width=device-width, initial-scale=1',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const googleClientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || '';

  return (
    <html lang="en" className="dark">
      <body className="bg-dark-bg">
        <GoogleOAuthProvider clientId={googleClientId}>
          <AuthProvider>
            <div className="min-h-screen flex flex-col">
              <Navbar />
              <main className="flex-1 overflow-auto">
                {children}
              </main>
            </div>
          </AuthProvider>
        </GoogleOAuthProvider>
      </body>
    </html>
  );
}
