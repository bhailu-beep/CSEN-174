// Test settings: "@/..." means src/, and tests run in a pretend browser (jsdom) so localStorage and the DOM work.
import { defineConfig } from "vitest/config";
import path from "path";

export default defineConfig({
  resolve: { alias: { "@": path.resolve(__dirname, "src") } },
  oxc: { jsx: { runtime: "automatic" } }, // so .tsx components compile without importing React
  test: {
    environment: "jsdom",
    include: ["tests/**/*.test.{ts,tsx}"],
    setupFiles: ["tests/setup.ts"],
  },
});
