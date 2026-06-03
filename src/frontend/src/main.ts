import { createApp } from "vue";
import { router } from "./router";
import App from "./App.vue";
// Design system (copié au prebuild depuis src/website/design-system.css).
import "./styles/design-system.css";
import "./styles/app.css";

createApp(App).use(router).mount("#app");
