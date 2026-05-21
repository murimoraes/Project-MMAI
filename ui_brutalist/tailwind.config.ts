import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Coinbase Design System
        "cb-bg": "#000000",
        "cb-surface": "#0A0B0D",
        "cb-elevated": "#141519",
        "cb-border": "rgba(255,255,255,0.08)",
        "cb-border-strong": "rgba(255,255,255,0.16)",
        "cb-blue": "#0052FF",
        "cb-blue-hover": "#1652F0",
        "cb-blue-muted": "rgba(0,82,255,0.12)",
        "cb-text": "#FFFFFF",
        "cb-muted": "#8A919E",
        "cb-dim": "#5B616E",
        "cb-success": "#05B169",
        "cb-success-muted": "rgba(5,177,105,0.12)",
        "cb-warning": "#F5A623",
        "cb-warning-muted": "rgba(245,166,35,0.12)",
        "cb-danger": "#DA3633",
        "cb-danger-muted": "rgba(218,54,51,0.12)",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "Consolas", "monospace"],
      },
      fontSize: {
        "2xs": "0.65rem",
      },
      borderRadius: {
        "cb": "12px",
        "cb-sm": "8px",
        "cb-lg": "16px",
      },
      boxShadow: {
        "cb": "0 1px 3px rgba(0,0,0,0.4), 0 1px 2px rgba(0,0,0,0.6)",
        "cb-lg": "0 4px 16px rgba(0,0,0,0.5)",
        "cb-blue": "0 0 0 3px rgba(0,82,255,0.25)",
      },
    },
  },
  plugins: [],
};

export default config;
