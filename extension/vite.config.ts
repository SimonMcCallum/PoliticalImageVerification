/// <reference types="vitest" />
import { defineConfig } from "vite";
import { crx } from "@crxjs/vite-plugin";
import manifest from "./public/manifest.json" with { type: "json" };

export default defineConfig({
  plugins: [crx({ manifest })],
  build: {
    outDir: "dist",
    emptyOutDir: true,
    sourcemap: true,
    rollupOptions: {
      input: {
        popup: "src/popup/index.html",
      },
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    coverage: {
      reporter: ["text", "html"],
      exclude: ["dist/", "public/", "**/*.config.*", "**/test/fixtures/**"],
    },
    include: ["test/**/*.test.ts"],
  },
});
