import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "path";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    host: true,
    port: 5173,
    strictPort: true,
    watch: {
      // Docker on Windows bind mounts: set CHOKIDAR_USEPOLLING=true in compose.
      usePolling: process.env.CHOKIDAR_USEPOLLING === "true",
    },
    proxy: {
      "/api": {
        // Docker: use VITE_PROXY_TARGET=http://backend:8000 (see docker-compose.yml)
        target:
          process.env.VITE_PROXY_TARGET ||
          process.env.VITE_API_URL ||
          "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes("node_modules")) {
            if (id.includes("recharts") || id.includes("d3-")) return "charts";
            if (id.includes("@tanstack/react-query")) return "query";
            if (id.includes("react-router") || id.includes("react-dom") || /\/react\//.test(id))
              return "vendor";
            if (id.includes("@hookform") || id.includes("zod")) return "forms";
          }
          if (id.includes("/features/reports/")) return "reports";
          if (id.includes("/features/settings/")) return "settings";
        },
      },
    },
    chunkSizeWarningLimit: 600,
  },
});
