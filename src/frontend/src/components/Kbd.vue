<script setup lang="ts">
import { computed } from "vue";

// Rend une combo canonique (ex: "ctrl+shift+f5") en segments <kbd> lisibles.
const props = defineProps<{ combo: string }>();

const LABELS: Record<string, string> = {
  ctrl: "Ctrl",
  alt: "Alt",
  shift: "Shift",
  win: "Win",
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
    <template v-for="(seg, i) in segments" :key="i">
      <kbd class="kbd">{{ seg }}</kbd>
      <span v-if="i < segments.length - 1" class="kbd-plus">+</span>
    </template>
  </span>
</template>

<style scoped>
.kbd-combo {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
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
.kbd-plus {
  color: var(--muted-2);
  font-size: var(--fs-xs);
}
</style>
