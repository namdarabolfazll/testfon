/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './static/js/**/*.js'
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Vazirmatn', 'ui-sans-serif', 'system-ui', 'sans-serif']
      },
      colors: {
        dara: {
          bg: '#FAF9F6',
          primary: '#1C1C1C',
          secondary: '#8A7968',
          accent: '#B88B5A',
          text: '#242424',
          muted: '#777777',
          border: '#E8E4DE',
          white: '#FFFFFF'
        }
      }
    }
  },
  plugins: []
}
