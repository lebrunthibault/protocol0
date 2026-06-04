import { createRouter, createWebHistory } from "vue-router";
import HomeView from "./views/HomeView.vue";

// History mode: the agent serves a catch-all SPA (any unknown path -> index.html),
// so the deep-link /shortcuts survives a refresh.
//
// /api-docs/ is NOT an SPA route: it's the vendored Swagger UI served
// statically by the agent (public/api-docs/, copied as-is into dist/), reachable
// even when Ableton is closed. The Help menu points to it directly.
export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "home", component: HomeView },
    {
      path: "/shortcuts",
      name: "keymapper",
      component: () => import("./views/KeymapperView.vue"),
    },
    // Everything else falls back to the home (the server already served index.html).
    { path: "/:pathMatch(.*)*", redirect: "/" },
  ],
});
