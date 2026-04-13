import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#09111b",
        panel: "#102235",
        ink: "#f4f1e8",
        accent: "#f0b04d",
        mint: "#8ad7c5",
        danger: "#f97373",
      },
      boxShadow: {
        glow: "0 20px 80px rgba(138, 215, 197, 0.15)",
      },
      backgroundImage: {
        "radial-grid":
          "radial-gradient(circle at top left, rgba(240,176,77,0.16), transparent 30%), radial-gradient(circle at 80% 20%, rgba(138,215,197,0.14), transparent 28%), linear-gradient(135deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0) 60%)",
      },
    },
  },
  plugins: [],
};

export default config;

