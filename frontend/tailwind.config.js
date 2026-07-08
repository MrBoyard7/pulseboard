/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef4ff",
          100: "#d9e6ff",
          500: "#3b6ef6",
          600: "#2c56d6",
          700: "#2244ad",
        },
        status: {
          onTrack: "#16a34a",
          atRisk: "#d97706",
          delayed: "#dc2626",
        },
      },
    },
  },
  plugins: [],
};
