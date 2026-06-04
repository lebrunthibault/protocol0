import { createRouter, createWebHistory } from "vue-router";
import HomeView from "./views/HomeView.vue";

// History mode : l'agent sert un catch-all SPA (tout chemin inconnu -> index.html),
// donc le deep-link /shortcuts survit à un refresh.
//
// /api-docs/ n'est PAS une route SPA : c'est la Swagger UI vendorée servie en
// statique par l'agent (public/api-docs/, copié tel quel dans dist/), accessible
// même Ableton fermé. Le menu Help y pointe directement.
export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "home", component: HomeView },
    {
      path: "/shortcuts",
      name: "keymapper",
      component: () => import("./views/KeymapperView.vue"),
    },
    // Tout le reste retombe sur la home (le serveur a déjà servi index.html).
    { path: "/:pathMatch(.*)*", redirect: "/" },
  ],
});
