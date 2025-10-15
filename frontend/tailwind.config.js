/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    // CRITICAL: This line must match where your React files are
    "./src/**/*.{js,ts,jsx,tsx}", 
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
