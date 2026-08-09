/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      boxShadow: {
        glass: '0 8px 32px rgba(31, 38, 135, 0.12)',
      },
      backdropBlur: {
        xs: '2px',
      },
      colors: {
        surface: {
          900: '#0b1120',
          800: '#10182c',
          700: '#172239',
          600: '#1e2b44',
        },
        accent: '#6d5cff',
      },
    },
  },
  plugins: [],
};
