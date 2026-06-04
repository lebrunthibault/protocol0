<script setup lang="ts">
import { computed } from "vue";

// Renders a canonical combo (e.g. "ctrl+shift+f5") into readable <kbd> segments.
const props = defineProps<{ combo: string }>();

const LABELS: Record<string, string> = {
  ctrl: "Ctrl",
  alt: "Alt",
  shift: "Shift",
  win: "Win",
  space: "Space",
  tab: "Tab",
  enter: "Enter",
  esc: "Esc",
  backspace: "Backspace",
  delete: "Delete",
  up: "↑",
  down: "↓",
  left: "←",
  right: "→",
  home: "Home",
  end: "End",
  pageup: "Page Up",
  pagedown: "Page Down",
};

const segments = computed(() =>
  props.combo
    .split("+")
    .filter(Boolean)
    .map((seg) => LABELS[seg] ?? seg.toUpperCase()),
);
</script>

<template>
  <span class="kbd-combo">
    <kbd v-for="(seg, i) in segments" :key="i" class="kbd">{{ seg }}</kbd>
  </span>
</template>

<style scoped>
.kbd-combo {
  display: inline-flex;
  align-items: center;
  gap: 2px;
}
.kbd {
  font-family: var(--font-mono);
  font-size: var(--fs-sm);
  color: var(--text);
  background: var(--panel-2);
  border: 1px solid var(--line-strong);
  border-bottom-width: 2px;
  border-radius: var(--radius-sm);
  padding: 2px 7px;
  min-width: 1.6em;
  text-align: center;
}
</style>
