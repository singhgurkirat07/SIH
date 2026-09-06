/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#0A2740", // deep navy
        accent: "#FF9933", // saffron accent
        "accent-red": "#D32F2F",
        "accent-green": "#388E3C",
        "bg-offwhite": "#FAFAFA",
      },
    },
  },
  plugins: [],
};
