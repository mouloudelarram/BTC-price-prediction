'use client';

export default function LoadingScreen() {
  return (
    <div className="min-h-screen bg-dark-bg flex items-center justify-center">
      <div className="text-center">
        <div className="text-4xl font-bold text-neon-blue mb-4">BNMP</div>
        <div className="flex items-center justify-center gap-2 mb-4">
          <div className="w-2 h-2 bg-neon-green rounded-full animate-pulse" />
          <div className="w-2 h-2 bg-neon-blue rounded-full animate-pulse" style={{ animationDelay: '0.1s' }} />
          <div className="w-2 h-2 bg-neon-red rounded-full animate-pulse" style={{ animationDelay: '0.2s' }} />
        </div>
        <p className="text-gray-400">Initializing dashboard...</p>
      </div>
    </div>
  );
}
