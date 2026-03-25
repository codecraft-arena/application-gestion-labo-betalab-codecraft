import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 30000,
    proxy: {
      "/api": { target: "http://localhost:8000", changeOrigin: true },
      "/connexion": { target: "http://localhost:8000", changeOrigin: true },
      "/submit": { target: "http://localhost:8000", changeOrigin: true },
      "/admin-login": { target: "http://localhost:8000", changeOrigin: true },
      "/logout": { target: "http://localhost:8000", changeOrigin: true },
      "/Report": { target: "http://localhost:8000", changeOrigin: true },
    },
  },
});
