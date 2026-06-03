import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// La SPA est servie par l'agent (exe PyInstaller) sous n'importe quel chemin via un
// catch-all -> base relative pour que les URLs d'assets résolvent partout.
// En dev, on proxifie /api et /status vers l'agent qui tourne sur :9010
// (`make agent` dans un autre terminal).
export default defineConfig({
  base: "./",
  plugins: [vue()],
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
  server: {
    port: 5173,
    proxy: {
      "/api": "http://127.0.0.1:9010",
      "/status": "http://127.0.0.1:9010",
    },
  },
});
