import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";


export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/assistant": "http://127.0.0.1:5001",
      "/booth": "http://127.0.0.1:5001",
      "/candidate": "http://127.0.0.1:5001",
      "/manifesto": "http://127.0.0.1:5001",
      "/health": "http://127.0.0.1:5001",
    },
  },
  test: {
    environment: "jsdom",
    setupFiles: "./vitest.setup.ts",
    globals: true,
  },
});
