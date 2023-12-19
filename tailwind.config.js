/** @type {import('tailwindcss').Config} */

module.exports = {
  content: [
      './templates/**/*.html',
      './node_modules/flowbite/**/*.js'
  ],
  variants: {
    extend: {
      transform: ['hover'],
    }
  },
  theme: {
    extend: {},
  },
  plugins: [
    require('flowbite/plugin')
  ],
}