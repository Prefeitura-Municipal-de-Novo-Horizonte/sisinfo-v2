/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
      './templates/**/*.html',
      './*/templates/**/*.html'
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // ==========================================
        // CATPPUCCIN THEME - Latte (Light) + Mocha (Dark)
        // https://github.com/catppuccin/catppuccin
        // ==========================================

        // Brand/Primary - Blue
        brand: {
          DEFAULT: '#1e66f5', // Latte Blue
          50: '#e6f0ff',
          100: '#cce0ff',
          200: '#99c2ff',
          300: '#66a3ff',
          400: '#3385ff',
          500: '#1e66f5', // Latte Blue (light mode)
          600: '#1a5ad6',
          700: '#164eb8',
          800: '#134299',
          900: '#0f377a',
          950: '#0b2b5c',
          // Dark mode variant
          dark: '#89b4fa', // Mocha Blue
        },

        // Catppuccin Latte (Light Theme)
        latte: {
          rosewater: '#dc8a78',
          flamingo: '#dd7878',
          pink: '#ea76cb',
          mauve: '#8839ef',
          red: '#d20f39',
          maroon: '#e64553',
          peach: '#fe640b',
          yellow: '#df8e1d',
          green: '#40a02b',
          teal: '#179299',
          sky: '#04a5e5',
          sapphire: '#209fb5',
          blue: '#1e66f5',
          lavender: '#7287fd',
          text: '#4c4f69',
          subtext1: '#5c5f77',
          subtext0: '#6c6f85',
          overlay2: '#7c7f93',
          overlay1: '#8c8fa1',
          overlay0: '#9ca0b0',
          surface2: '#acb0be',
          surface1: '#bcc0cc',
          surface0: '#ccd0da',
          base: '#eff1f5',
          mantle: '#e6e9ef',
          crust: '#dce0e8',
        },

        // Catppuccin Mocha (Dark Theme)
        mocha: {
          rosewater: '#f5e0dc',
          flamingo: '#f2cdcd',
          pink: '#f5c2e7',
          mauve: '#cba6f7',
          red: '#f38ba8',
          maroon: '#eba0ac',
          peach: '#fab387',
          yellow: '#f9e2af',
          green: '#a6e3a1',
          teal: '#94e2d5',
          sky: '#89dceb',
          sapphire: '#74c7ec',
          blue: '#89b4fa',
          lavender: '#b4befe',
          text: '#cdd6f4',
          subtext1: '#bac2de',
          subtext0: '#a6adc8',
          overlay2: '#9399b2',
          overlay1: '#7f849c',
          overlay0: '#6c7086',
          surface2: '#585b70',
          surface1: '#45475a',
          surface0: '#313244',
          base: '#1e1e2e',
          mantle: '#181825',
          crust: '#11111b',
        },

        // Semantic Colors - for status badges, alerts, etc.
        success: {
          light: '#40a02b', // Latte green
          dark: '#a6e3a1',   // Mocha green
          DEFAULT: '#40a02b',
        },
        warning: {
          light: '#df8e1d', // Latte yellow
          dark: '#f9e2af',   // Mocha yellow
          DEFAULT: '#df8e1d',
        },
        danger: {
          light: '#d20f39', // Latte red
          dark: '#f38ba8',   // Mocha red
          DEFAULT: '#d20f39',
        },
        info: {
          light: '#04a5e5', // Latte sky
          dark: '#89dceb',   // Mocha sky
          DEFAULT: '#04a5e5',
        },
      },
    },
  },
  plugins: [],
}
