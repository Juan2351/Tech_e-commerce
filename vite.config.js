import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import prefixSelector from "postcss-prefix-selector";

export default defineConfig({
  base: "/static/dist/",
  plugins: [react()],
  css: {
    postcss: {
      plugins: [
        prefixSelector({
          prefix: ".bootstrap-scope",
          transform(prefix, selector, prefixedSelector) {
            if (selector === ":root") return prefix;
            if (selector.startsWith("html") || selector.startsWith("body")) {
              return `${prefix} ${selector}`;
            }
            return prefixedSelector;
          },
        }),
      ],
    },
  },
  build: {
    outDir: "static/dist",
    emptyOutDir: true,
    rollupOptions: {
      input: fileURLToPath(new URL("./static/js/app.js", import.meta.url)),
      output: {
        entryFileNames: "app.js",
        chunkFileNames: "chunks/[name].js",
        assetFileNames: "assets/[name][extname]",
      },
    },
  },
});
