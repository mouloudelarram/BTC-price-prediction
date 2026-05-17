# BNMP Dashboard - Development Instructions

## Project Overview

This is a production-grade financial dashboard for BTC Next Move Prediction (BNMP) system. It's a Next.js 14 + React 18 application with TypeScript, TailwindCSS, and Zustand state management.

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **UI**: React 18 + TypeScript
- **Styling**: TailwindCSS with dark mode
- **State Management**: Zustand
- **API Client**: Axios
- **Charts**: Recharts
- **Authentication**: Google OAuth
- **Icons**: React Icons

## Project Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── page.tsx           # Main dashboard
│   ├── layout.tsx         # Root layout
│   ├── globals.css        # Global styles
│   ├── signals/           # Signals history
│   ├── correlation/       # Correlation analysis
│   ├── mood/              # Social sentiment
│   └── dl/                # Deep learning models
├── components/            # Reusable React components
│   ├── Navbar.tsx         # Top navigation
│   ├── Dashboard.tsx      # Main dashboard layout
│   ├── AuthProvider.tsx   # Auth context
│   ├── LoginScreen.tsx    # Google OAuth login
│   ├── LoadingScreen.tsx  # Loading state
│   ├── panels/            # Dashboard panels
│   │   ├── FinalPredictionPanel.tsx
│   │   ├── CorrelationPanel.tsx
│   │   ├── DeepLearningPanel.tsx
│   │   └── MoodPanel.tsx
│   ├── SkeletonLoader.tsx # Loading skeleton
│   ├── ErrorBanner.tsx    # Error notifications
│   └── RefreshButton.tsx  # Refresh data button
├── services/              # API clients
│   └── apiClient.ts       # Axios-based API client
├── store/                 # Zustand stores
│   ├── authStore.ts       # Authentication state
│   └── dashboardStore.ts  # Dashboard data state
├── hooks/                 # Custom React hooks
│   └── useHealthCheck.ts  # API health monitoring
├── types/                 # TypeScript interfaces
│   └── index.ts           # All type definitions
└── utils/                 # Utility functions
    └── styling.ts         # Styling helpers
```

## Setup Instructions

### 1. Install Dependencies

```bash
npm install
# or
yarn install
# or
pnpm install
```

### 2. Environment Configuration

Create a `.env.local` file in the root directory (copy from `.env.example`):

```env
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_google_client_id_here
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=BNMP Dashboard
NEXT_PUBLIC_API_POLLING_INTERVAL=60000
```

**Get Google Client ID:**
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable "Google+ API"
4. Create OAuth 2.0 credentials (Web Application)
5. Add `http://localhost:3000` to authorized JavaScript origins
6. Add `http://localhost:3000/` to authorized redirect URIs
7. Copy the Client ID to `.env.local`

### 3. Run Development Server

```bash
npm run dev
```

Navigate to `http://localhost:3000` in your browser.

## API Integration

The dashboard connects to backend APIs for:

- **Final Signal**: `/final/signal` - Combined AI prediction
- **Correlation**: `/correlation/summary` - Market correlation analysis
- **Deep Learning**: `/dl/predict` - ML model predictions
- **Mood**: `/mood/sentiment` - Social sentiment analysis
- **Health Check**: `/health` - API availability status

### API Response Format

See `src/types/index.ts` for all interface definitions.

## Authentication Flow

1. User visits the app
2. Redirected to Google OAuth login if not authenticated
3. User grants permissions
4. Frontend receives access token
5. Token stored in localStorage
6. Dashboard loads automatically
7. All API calls include Authorization header

## Key Features

### 🎨 UI/UX
- Dark mode with neon accents (green=BUY, red=SELL, blue=info)
- Glassmorphism design with blur effects
- Smooth animations and transitions
- Loading skeletons for data states
- Responsive design (mobile, tablet, desktop)

### 📊 Dashboard Panels
- **Final Prediction**: Hero card with confidence score
- **Correlation Engine**: Top correlated indices with chart
- **Deep Learning**: Model predictions and confidence
- **Social Mood**: Sentiment gauge and trend indicator

### 🔄 Data Management
- Automatic polling (configurable interval)
- Manual refresh button
- Error handling with retry
- Last updated timestamp
- Fallback for failed API calls

### 🔐 Security
- Google OAuth authentication
- Bearer token authorization
- Secure token storage
- Protected routes (redirects to login if needed)

## Development Guidelines

### Adding New Pages

Create a new directory in `src/app/` with a `page.tsx` file:

```typescript
export default function NewPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Your content */}
    </div>
  );
}
```

### Creating New Components

Place reusable components in `src/components/`:

```typescript
'use client';

interface MyComponentProps {
  title: string;
}

export default function MyComponent({ title }: MyComponentProps) {
  return <div className="glass-lg rounded-2xl p-6">{title}</div>;
}
```

### Adding API Endpoints

Extend `src/services/apiClient.ts`:

```typescript
async getNewData(): Promise<NewDataResponse> {
  try {
    const response = await this.client.get('/new/endpoint');
    return response.data;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}
```

### Using Global State

Use Zustand stores:

```typescript
import { useDashboardStore } from '@/store/dashboardStore';

const { finalSignal, isLoading, error, fetchAllData } = useDashboardStore();
```

## Styling

### Tailwind Classes
- **Colors**: `text-neon-green`, `text-neon-red`, `text-neon-blue`
- **Backgrounds**: `bg-dark-bg`, `bg-dark-panel`
- **Glass Effect**: `.glass` (for glassmorphism)
- **Glow Effects**: `glow-green`, `glow-red`, `glow-blue`
- **Animations**: `animate-fade-in`, `animate-slide-up`

### Custom CSS
See `src/app/globals.css` for custom animations and utilities.

## Performance Optimization

- Lazy loading for charts and images
- Optimized API polling (configurable interval)
- Image optimization with Next.js Image component
- Code splitting with Next.js App Router
- Memoization of expensive calculations

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile browsers (iOS Safari, Chrome Mobile)
- Minimum: ES2020 support

## Deployment

### Vercel (Recommended)
```bash
vercel deploy
```

### Docker
Create a `Dockerfile`:
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY . .
RUN npm install
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## Troubleshooting

### "Google Client ID not found"
- Ensure `.env.local` has `NEXT_PUBLIC_GOOGLE_CLIENT_ID`
- Restart dev server after updating env

### API calls failing
- Check `NEXT_PUBLIC_API_BASE_URL` in `.env.local`
- Verify backend is running on correct port
- Check health indicator in navbar (red = offline)

### Styling issues
- Run `npm run build` to check for Tailwind errors
- Clear `.next` folder and restart dev server
- Ensure PostCSS is configured correctly

## Building for Production

```bash
npm run build
npm run start
```

## Common Commands

```bash
npm run dev         # Start dev server
npm run build       # Build for production
npm start          # Start production server
npm run lint       # Run ESLint
npm run type-check # Run TypeScript compiler
```

## Additional Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [TailwindCSS Documentation](https://tailwindcss.com)
- [Zustand Documentation](https://github.com/pmndrs/zustand)
- [Recharts Documentation](https://recharts.org)

## Support

For issues or questions about the frontend, refer to the backend API documentation or contact the development team.
