import { createRouter, createWebHistory } from "vue-router";
import HomeView from "./views/HomeView.vue";

// History mode: the agent serves a catch-all SPA (any unknown path -> index.html),
// so the deep-link /shortcuts survives a refresh.
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
