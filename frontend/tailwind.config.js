/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Brand palette
        primary: {
          50: '#e9f7f6',
          100: '#c9ebe8',
          200: '#98d9d3',
          300: '#67c6bd',
          400: '#36b4a8',
          500: '#14a39a',
          600: '#0D9488', // teal
          700: '#0b7a70',
          800: '#0a5f58',
          900: '#084b46',
        },
        secondary: {
          50: '#e9eef5',
          100: '#c8d4e6',
          200: '#97adcf',
          300: '#6686b8',
          400: '#3a5c91',
          500: '#284a7e',
          600: '#1E3A5F', // deep navy
          700: '#18304f',
          800: '#12263f',
          900: '#0c1b2e',
        },
        accent: {
          50: '#fff1ef',
          100: '#ffd9d3',
          200: '#ffb5ab',
          300: '#ff8f83',
          400: '#fb7a6e',
          500: '#F97362', // coral
          600: '#ea5a47',
          700: '#cf4736',
          800: '#a53a2d',
          900: '#7b2c22',
        },
        support: {
          50: '#F7FBF9', // soft sand / very light mint-sand
          100: '#F1F8F5',
          200: '#e7f1ec',
          300: '#d9e8e1',
          400: '#c9ded5',
          500: '#b9d3c8',
          600: '#9fbeb1',
          700: '#85a89a',
          800: '#6a9183',
          900: '#52786b',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'bounce-in': 'bounceIn 0.6s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        bounceIn: {
          '0%': { transform: 'scale(0.3)', opacity: '0' },
          '50%': { transform: 'scale(1.05)' },
          '70%': { transform: 'scale(0.9)' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
