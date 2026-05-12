import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        asphalt: "#1a1a1a",
        neon: "#ccff00",
        steel: "#2a2a2a",
        dim: "#404040",
        ghost: "#888888",
      },
      fontFamily: {
        mono: ["JetBrains Mono", "Fira Code", "Consolas", "monospace"],
        display: ["Inter", "system-ui", "sans-serif"],
      },
      fontSize: {
        "2xs": "0.65rem",
      },
    },
  },
  plugins: [],
};

export default config;
