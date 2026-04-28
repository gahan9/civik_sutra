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
    exclude: [
      "**/node_modules/**",
      "**/dist/**",
      "**/e2e/**",
      "**/playwright-report/**",
    ],
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
      include: ["src/**/*.{ts,tsx}"],
      exclude: ["src/**/*.test.{ts,tsx}", "src/main.tsx", "src/vite-env.d.ts"],
      // Baseline while the suite grows; raise toward 60–90% as in Nirvachan-style repos.
      thresholds: {
        statements: 6,
        branches: 5,
        functions: 2,
        lines: 7,
      },
    },
  },
});
