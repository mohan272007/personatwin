/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        base: "#0B0E17",
        surface: "#121726",
        surface2: "#1A2033",
        border: "#232B42",
        violet: "#8B5CF6",
        cyan: "#22D3EE",
        amber: "#F5B841",
        ink: "#E7E9EE",
        muted: "#8791A8",
      },
      fontFamily: {
        display: ["'Space Grotesk'", "sans-serif"],
        body: ["'Inter'", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
      },
      boxShadow: {
        glow: "0 0 40px rgba(139, 92, 246, 0.25)",
      },
    },
  },
  plugins: [],
};
