/** @type {import('tailwindcss').Config} */

module.exports = {
  content: ["./**/*.{html,js}", "./node_modules/flowbite/**/*.js"],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1440px",
      },
      extend: {
        fontFamily: {
          primary: ["Poppins"],
        },
      },
    },
    extend: {
      // backgroundImage: {
      //   "category-item-gradient":
      //     "linear-gradient(45deg, #5033C3 0%, rgba(80, 51, 195, 0.20) 100%);",
      // },
      colors: {
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        primary: "hsl(var(--primary))",
        secondary: "hsl(var(--secondary))",
        main: "hsl(var(--main-color))",
        personred: "hsl(var(--red))",
        personyellow: "hsl(var(--yellow))",
        personcornflower: "hsl(var(--corn-flower))",
        personcream: "hsl(var(--cream))",
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: 0 },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: 0 },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("flowbite/plugin")],
};