<script setup lang="ts">
import { ref } from "vue";
import { useComboCapture } from "../composables/useComboCapture";

// Recherche : texte (libellé/combo) OU par frappe (capture une combo -> filtre).
const text = defineModel<string>("text", { default: "" });
const byHotkey = defineModel<string>("hotkey", { default: "" });

const capturing = ref(false);
const capture = useComboCapture();

function toggleHotkey() {
  capturing.value = !capturing.value;
  if (capturing.value) {
    capture.start();
  } else {
    byHotkey.value = "";
    capture.clear();
  }
}

function onHotkeyKeydown(e: KeyboardEvent) {
  capture.onKeydown(e);
  if (capture.combo.value) byHotkey.value = capture.combo.value;
}
</script>

<template>
  <div class="search">
    <input
      class="input search-text"
      v-model="text"
      type="search"
      placeholder="Search shortcuts…"
      :disabled="capturing"
    />
    <button
      type="button"
      class="btn btn-ghost search-toggle"
      :class="{ 'search-toggle--on': capturing }"
      @click="toggleHotkey"
    >
      {{ capturing ? "✕ by key" : "🔍 by key" }}
    </button>
    <span
      v-if="capturing"
      class="capture search-capture"
      tabindex="0"
      @keydown="onHotkeyKeydown"
    >
      {{ byHotkey || "press a combo…" }}
    </span>
  </div>
</template>

<style scoped>
.search {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}
.search-text {
  flex: 1;
}
.search-toggle {
  white-space: nowrap;
}
.search-toggle--on {
  border-color: var(--accent-line);
  color: var(--accent-soft);
}
.search-capture {
  min-width: 10em;
}
</style>
