/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './pages/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        blue: {
          50:  '#e7eef7',
          100: '#c5d6ea',
          200: '#a2bddc',
          300: '#7fa5cf',
          400: '#5c8dc2',
          500: '#3964a1',
          600: '#0F3E69', // primary
          700: '#0c3050',
          800: '#092137',
          900: '#05111d',
        },
      },
    },
  },

  plugins: [],
}
