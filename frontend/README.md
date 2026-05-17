# BNMP Dashboard - Production-Grade Financial Dashboard

A modern, production-grade financial web dashboard for the BNMP (BTC Next Move Prediction) system. Built with Next.js 14, React 18, and TailwindCSS with institutional-grade UI inspired by Binance, TradingView, and Bloomberg Terminal.

![React](https://img.shields.io/badge/React-18.0+-61DAFB?logo=react)
![Next.js](https://img.shields.io/badge/Next.js-14.0+-000000?logo=nextjs)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?logo=typescript)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.0+-38B2AC?logo=tailwindcss)

## 🎯 Features

### ✨ Core Features
- **Google OAuth Authentication** - Secure user authentication
- **Real-time AI Predictions** - BUY/SELL signals with confidence scores
- **Multi-Model Analysis** - Correlation engine, deep learning, social mood
- **Institutional UI** - Dark mode with neon accents and glassmorphism
- **Live Dashboard** - Auto-refresh with manual controls
- **Responsive Design** - Desktop, tablet, and mobile support
- **Error Handling** - Graceful degradation with loading states

### 📊 Dashboard Components
1. **Final Prediction Panel** - Main signal with confidence score
2. **Correlation Engine** - Top correlated indices with bar charts
3. **Deep Learning Model** - ML model predictions and explanations
4. **Social Mood Engine** - Sentiment gauge and trend indicators

### 🎨 Design System
- **Dark Mode** - Black and deep navy backgrounds
- **Neon Accents** - Green (BUY), Red (SELL), Blue (info)
- **Glassmorphism** - Frosted glass effect with transparency
- **Smooth Animations** - Fade-in and slide-up transitions
- **Premium Feel** - Institutional trading platform aesthetic

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- npm, yarn, or pnpm
- Google OAuth credentials

### Installation

1. **Clone and navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your credentials
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

5. **Open in browser**
   - Navigate to `http://localhost:3000`
   - Sign in with Google
   - View the dashboard!

## 📋 Configuration

### Environment Variables
Create a `.env.local` file:

```env
# Google OAuth
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_google_client_id

# Backend API
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Settings
NEXT_PUBLIC_APP_NAME=BNMP Dashboard
NEXT_PUBLIC_API_POLLING_INTERVAL=60000
```

### Get Google Client ID
1. Visit [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable "Google+ API"
4. Create OAuth 2.0 Web credentials
5. Add `http://localhost:3000` to authorized JavaScript origins
6. Copy Client ID to `.env.local`

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js 14 pages
│   │   ├── page.tsx           # Dashboard
│   │   ├── layout.tsx         # Root layout
│   │   ├── globals.css        # Global styles
│   │   └── [feature]/page.tsx # Feature pages
│   ├── components/            # React components
│   │   ├── panels/            # Dashboard panels
│   │   └── *.tsx              # Reusable components
│   ├── services/              # API integration
│   │   └── apiClient.ts       # Axios client
│   ├── store/                 # Zustand state
│   │   ├── authStore.ts       # Auth state
│   │   └── dashboardStore.ts  # Data state
│   ├── hooks/                 # Custom React hooks
│   ├── types/                 # TypeScript interfaces
│   └── utils/                 # Utilities
├── public/                    # Static assets
├── package.json              # Dependencies
├── tsconfig.json             # TypeScript config
├── tailwind.config.js        # Tailwind config
└── next.config.js            # Next.js config
```

## 🔌 API Integration

### Supported Endpoints

| Endpoint | Purpose | Response |
|----------|---------|----------|
| `GET /final/signal` | Combined AI prediction | Signal + confidence |
| `GET /correlation/summary` | Market correlation | Indices + correlations |
| `GET /dl/predict` | Deep learning prediction | BUY/SELL + confidence |
| `GET /mood/sentiment` | Social sentiment | Score + classification |
| `GET /health` | API health check | Status |

### Request/Response Example

```typescript
// Request
const response = await apiClient.getFinalSignal();

// Response
{
  "signal": "BUY",
  "confidence": 0.87,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🔐 Authentication Flow

```
1. User visits app
   ↓
2. Check localStorage for token
   ↓
3. If no token → Show Login Screen
   ↓
4. User clicks "Sign in with Google"
   ↓
5. Google OAuth popup
   ↓
6. User grants permissions
   ↓
7. Frontend receives access token
   ↓
8. Store token + user info in localStorage
   ↓
9. Auto-load dashboard
   ↓
10. Fetch all API data
```

## 🛠 Development

### Commands

```bash
npm run dev         # Start development server
npm run build       # Production build
npm start          # Start production server
npm run lint       # Run ESLint
npm run type-check # Check TypeScript
```

### Adding New Components

```typescript
'use client';

interface MyProps {
  title: string;
}

export default function MyComponent({ title }: MyProps) {
  return (
    <div className="glass-lg rounded-2xl p-6">
      <h3 className="text-lg font-semibold text-white">{title}</h3>
    </div>
  );
}
```

### Using Global State

```typescript
import { useDashboardStore } from '@/store/dashboardStore';

export default function MyPage() {
  const { finalSignal, isLoading, fetchAllData } = useDashboardStore();
  
  return <div>{/* Your JSX */}</div>;
}
```

### Styling Classes

```typescript
// Colors
className="text-neon-green"  // BUY signal
className="text-neon-red"    // SELL signal
className="text-neon-blue"   // Info

// Backgrounds
className="bg-dark-bg"       // Page background
className="bg-dark-panel"    // Panel background

// Effects
className="glass-lg"         // Glassmorphism
className="glow-green"       // Green glow effect
className="animate-slide-up" // Animation
```

## 📊 Performance

- ⚡ Initial load: <2s target
- 📦 Lazy loading for charts
- 💾 API response caching
- 🎬 Smooth 60fps animations
- 📱 Responsive across all devices

## 🌐 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers (iOS Safari 14+, Chrome Mobile)

## 🚢 Deployment

### Vercel (Recommended)
```bash
vercel deploy
```

### Docker
```bash
docker build -t bnmp-dashboard .
docker run -p 3000:3000 bnmp-dashboard
```

### Traditional Hosting
```bash
npm run build
npm start
```

## 📚 Technology Stack

| Category | Technology |
|----------|------------|
| Framework | Next.js 14 |
| UI Library | React 18 |
| Language | TypeScript |
| Styling | TailwindCSS 3 |
| State | Zustand |
| HTTP Client | Axios |
| Charts | Recharts |
| Auth | Google OAuth |
| Icons | React Icons |

## 🐛 Troubleshooting

### Issue: "Google Client ID not found"
**Solution**: Ensure `.env.local` contains `NEXT_PUBLIC_GOOGLE_CLIENT_ID`

### Issue: API calls failing
**Solution**: 
- Check `NEXT_PUBLIC_API_BASE_URL` points to correct backend
- Verify backend is running
- Check health indicator in navbar

### Issue: Styling not applying
**Solution**:
- Delete `.next` folder
- Restart dev server
- Clear browser cache

## 📖 Documentation

- [Development Guide](./.github/copilot-instructions.md)
- [Next.js Docs](https://nextjs.org/docs)
- [React Docs](https://react.dev)
- [TailwindCSS Docs](https://tailwindcss.com)

## 📄 License

Proprietary - All rights reserved

## 👥 Team

- **Senior Frontend Engineer** - UI/UX Implementation
- **Product Designer** - Design System
- **Backend Team** - API Integration

## 📞 Support

For issues or questions, refer to:
- Backend API documentation
- Development guide in `.github/copilot-instructions.md`
- Team Slack channel

---

**Status**: ✅ Production Ready  
**Last Updated**: May 2026  
**Version**: 1.0.0
