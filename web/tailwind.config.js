/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#020617",
        foreground: "#f8fafc"
      }
    }
  },
  plugins: [require("tailwindcss-animate")]
};
