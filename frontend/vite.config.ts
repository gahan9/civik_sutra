import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";


export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/booth": "http://127.0.0.1:5001",
      "/health": "http://127.0.0.1:5001",
    },
  },
  test: {
    environment: "jsdom",
    setupFiles: "./vitest.setup.ts",
    globals: true,
  },
});
