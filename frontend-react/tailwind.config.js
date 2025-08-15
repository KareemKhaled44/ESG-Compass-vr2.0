/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        inter: ['Inter', 'sans-serif'],
        sans: ['Inter', 'sans-serif']
      },
      colors: {
        'brand-green': '#2EC57D',
        'brand-blue': '#3DAEFF',
        'brand-teal': '#20C5C5',
        'surface-glass': 'rgba(30, 32, 44, 0.24)',
        'text-high': '#F8F9FA',
        'text-muted': 'rgba(248, 249, 250, 0.72)'
      },
      backdropBlur: {
        glass: '12px'
      },
      borderRadius: {
        card: '18px'
      }
    },
  },
  plugins: [],
}