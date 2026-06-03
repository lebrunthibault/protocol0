import { createRouter, createWebHistory } from "vue-router";
import HomeView from "./views/HomeView.vue";

// History mode : l'agent sert un catch-all SPA (tout chemin inconnu -> index.html),
// donc les deep-links /shortcuts et /api-docs survivent à un refresh.
export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "home", component: HomeView },
    {
      path: "/shortcuts",
      name: "keymapper",
      component: () => import("./views/KeymapperView.vue"),
    },
    {
      path: "/api-docs",
      name: "api-docs",
      component: () => import("./views/ApiDocsView.vue"),
    },
    // Tout le reste retombe sur la home (le serveur a déjà servi index.html).
    { path: "/:pathMatch(.*)*", redirect: "/" },
  ],
});
