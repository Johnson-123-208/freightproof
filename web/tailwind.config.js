/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        steel: {
          50: "#f4f6f8",
          100: "#e4e9ed",
          200: "#c5cfd8",
          300: "#9aabb9",
          400: "#6f8496",
          500: "#526678",
          600: "#3f5160",
          700: "#34424e",
          800: "#2c3842",
          900: "#272f37",
          950: "#1a2026",
        },
        accent: {
          DEFAULT: "#3d6b7a",
          light: "#5a8f9e",
          muted: "#2a4a54",
        },
      },
      fontFamily: {
        sans: ["IBM Plex Sans", "system-ui", "sans-serif"],
        mono: ["IBM Plex Mono", "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
};