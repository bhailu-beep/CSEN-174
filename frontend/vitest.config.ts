// Test settings: "@/..." means src/, and tests run in a pretend browser (jsdom) so localStorage works.
import { defineConfig } from "vitest/config";
import path from "path";

export default defineConfig({
  resolve: { alias: { "@": path.resolve(__dirname, "src") } },
  test: { environment: "jsdom", include: ["tests/**/*.test.{ts,tsx}"] },
});
