/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Neon accents
        'neon-green': '#00ff41',
        'neon-red': '#ff3333',
        'neon-blue': '#00d4ff',
        // Dark backgrounds
        'dark-bg': '#0a0e27',
        'dark-panel': '#1a1f3a',
        'dark-border': '#2d3561',
      },
      backdropBlur: {
        xs: '2px',
        sm: '4px',
      },
      boxShadow: {
        'glow-green': '0 0 20px rgba(0, 255, 65, 0.3)',
        'glow-red': '0 0 20px rgba(255, 51, 51, 0.3)',
        'glow-blue': '0 0 20px rgba(0, 212, 255, 0.3)',
      },
    },
  },
  darkMode: 'class',
  plugins: [],
};
