/** @type {import('tailwindcss').Config} */

module.exports = {
  content: ['./src/**/*.{html,js}', './node_modules/flowbite/**/*.js'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {"50":"#eef2ff","100":"#e0e7ff","200":"#c7d2fe","300":"#a5b4fc","400":"#818cf8","500":"#6366f1","600":"#4f46e5","700":"#4338ca","800":"#3730a3","900":"#312e81","950":"#1e1b4b"}
      }
    },
    fontFamily: {
      'body': [
    'Poppins'
  ],
      'sans': [
    'Poppins'
  ]
    }
  },
  plugins: [require('flowbite/plugin')]
}
