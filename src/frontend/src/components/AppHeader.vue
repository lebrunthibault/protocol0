<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import { DOCS_URL } from "../config";
import StatusPill from "./StatusPill.vue";

// "API docs" + "Docs" live behind a help (?) menu on the right of the header so the
// nav stays focused on the one thing you act on (the keymapper). API docs points to
// the vendored Swagger UI the agent serves on /api-docs/.
const open = ref(false);
const root = ref<HTMLElement | null>(null);

function close(): void {
  open.value = false;
}

// Close on outside-click / Escape (a dropdown that only closes on re-click feels stuck).
function onDocClick(e: MouseEvent): void {
  if (root.value && !root.value.contains(e.target as Node)) close();
}
function onKey(e: KeyboardEvent): void {
  if (e.key === "Escape") close();
}

onMounted(() => {
  document.addEventListener("click", onDocClick);
  document.addEventListener("keydown", onKey);
});
onBeforeUnmount(() => {
  document.removeEventListener("click", onDocClick);
  document.removeEventListener("keydown", onKey);
});
</script>

<template>
  <header>
    <div class="wrap">
      <nav class="nav">
        <RouterLink to="/" class="brand">
          <span class="dot">P0</span>
          <span>Protocol 0</span>
        </RouterLink>
        <div class="nav-links">
          <RouterLink to="/shortcuts">Keymapper</RouterLink>
        </div>
        <div class="nav-right">
          <StatusPill />
          <div ref="root" class="help">
            <button
              class="help-btn"
              type="button"
              aria-label="Help"
              :aria-expanded="open"
              @click="open = !open"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <circle cx="12" cy="12" r="10" />
                <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
                <line x1="12" y1="17" x2="12.01" y2="17" />
              </svg>
            </button>
            <div v-if="open" class="help-menu" role="menu">
              <a class="help-item" href="/api-docs/index.html" target="_blank"
                rel="noopener" role="menuitem" @click="close">API docs</a>
              <a class="help-item" :href="DOCS_URL" target="_blank" rel="noopener"
                role="menuitem" @click="close">Docs</a>
            </div>
          </div>
        </div>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.help {
  position: relative;
  display: flex;
  align-items: center;
}
.help-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  padding: 0;
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  background: transparent;
  color: var(--muted);
  cursor: pointer;
  transition: color var(--t), background var(--t), border-color var(--t);
}
.help-btn:hover,
.help-btn[aria-expanded="true"] {
  color: var(--text);
  background: rgba(255, 255, 255, 0.04);
  border-color: var(--line);
}
.help-btn svg {
  width: 17px;
  height: 17px;
}
.help-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 150px;
  display: flex;
  flex-direction: column;
  padding: var(--space-2);
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-pop, 0 8px 24px rgba(0, 0, 0, 0.45));
  z-index: 60;
}
.help-item {
  padding: 7px var(--space-3);
  border-radius: var(--radius-sm);
  font-size: var(--fs-base);
  color: var(--muted);
  transition: color var(--t), background var(--t);
}
.help-item:hover {
  color: var(--text);
  background: rgba(255, 255, 255, 0.05);
}
</style>
