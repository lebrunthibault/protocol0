<script setup lang="ts">
import { nextTick, ref } from "vue";
import { useComboCapture } from "../composables/useComboCapture";

// Search: text (label/combo) OR by keystroke (captures a combo -> filters).
// Two distinct modes: in "by key" mode we capture the combo (so we don't override
// a ctrl+c / ctrl+v typed in the text field). Toggle via the keyboard icon on the right.
const text = defineModel<string>("text", { default: "" });
const byHotkey = defineModel<string>("hotkey", { default: "" });

const capturing = ref(false);
const capture = useComboCapture();
const captureEl = ref<HTMLSpanElement | null>(null);

function toggleHotkey() {
  capturing.value = !capturing.value;
  if (capturing.value) {
    byHotkey.value = "";
    capture.start();
    // Direct focus: the first keystroke is captured without re-clicking.
    nextTick(() => captureEl.value?.focus());
  } else {
    byHotkey.value = "";
    capture.clear();
  }
}

function onHotkeyKeydown(e: KeyboardEvent) {
  capture.onKeydown(e);
  if (capture.combo.value) byHotkey.value = capture.combo.value;
}

// Inline cross: clears the active field. In "by key" mode, also switches back to text mode.
function clearActive() {
  if (capturing.value) {
    capturing.value = false;
    capture.clear();
    byHotkey.value = "";
  } else {
    text.value = "";
  }
}
</script>

<template>
  <div class="search">
    <div class="search-field">
      <input
        v-if="!capturing"
        class="input search-text"
        v-model="text"
        type="text"
        placeholder="Search shortcuts…"
      />
      <span
        v-else
        ref="captureEl"
        class="capture search-capture"
        tabindex="0"
        @keydown="onHotkeyKeydown"
      >
        {{ byHotkey || "press a combo…" }}
      </span>
      <button
        v-if="capturing ? byHotkey : text"
        type="button"
        class="search-clear"
        aria-label="Clear"
        @click="clearActive"
      >
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <line x1="18" y1="6" x2="6" y2="18" />
          <line x1="6" y1="6" x2="18" y2="18" />
        </svg>
      </button>
    </div>
    <button
      type="button"
      class="btn btn-ghost search-toggle"
      :class="{ 'search-toggle--on': capturing }"
      title="Search by pressing a combo"
      aria-label="Search by key"
      @click="toggleHotkey"
    >
      <svg
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
      >
        <rect x="2" y="6" width="20" height="12" rx="2" />
        <line x1="6" y1="10" x2="6" y2="10" />
        <line x1="10" y1="10" x2="10" y2="10" />
        <line x1="14" y1="10" x2="14" y2="10" />
        <line x1="18" y1="10" x2="18" y2="10" />
        <line x1="8" y1="14" x2="16" y2="14" />
      </svg>
    </button>
  </div>
</template>

<style scoped>
.search {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}
.search-field {
  position: relative;
  flex: 1;
  display: flex;
}
.search-text,
.search-capture {
  flex: 1;
}
/* Inline cross, on the right inside the field. */
.search-clear {
  position: absolute;
  top: 50%;
  right: 8px;
  transform: translateY(-50%);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  padding: 0;
  border: none;
  background: transparent;
  color: var(--muted);
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: color var(--t), background var(--t);
}
.search-clear:hover {
  color: var(--text);
  background: rgba(255, 255, 255, 0.08);
}
.search-clear svg {
  width: 13px;
  height: 13px;
}
/* Leaves room for the cross so it doesn't overlap the text. */
.search-field :deep(.input),
.search-capture {
  padding-right: 32px;
}
.search-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 9px;
}
.search-toggle svg {
  width: 17px;
  height: 17px;
}
.search-toggle--on {
  color: var(--accent-soft);
}
</style>
