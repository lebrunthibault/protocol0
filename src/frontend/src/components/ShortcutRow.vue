<script setup lang="ts">
import type { Binding } from "../api/types";
import Kbd from "./Kbd.vue";

defineProps<{ binding: Binding }>();
const emit = defineEmits<{ edit: []; remove: [] }>();

function paramSummary(params: Record<string, string>): string {
  const entries = Object.entries(params);
  if (!entries.length) return "";
  return entries.map(([k, v]) => `${k}: ${v}`).join(", ");
}
</script>

<template>
  <div class="row">
    <div class="row-main">
      <div class="row-action">{{ binding.action }}</div>
      <div v-if="Object.keys(binding.params).length" class="row-params">
        {{ paramSummary(binding.params) }}
      </div>
    </div>
    <Kbd :combo="binding.combo" />
    <div class="row-actions">
      <button type="button" class="row-btn" @click="emit('edit')">Edit</button>
      <button type="button" class="row-btn row-btn--reset" title="Remove" @click="emit('remove')">
        ↺
      </button>
    </div>
  </div>
</template>

<style scoped>
.row {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--line);
}
.row:last-child {
  border-bottom: none;
}
.row-main {
  flex: 1;
  min-width: 0;
}
.row-action {
  font-size: var(--fs-base);
  color: var(--text);
}
.row-params {
  font-family: var(--font-mono);
  font-size: var(--fs-xs);
  color: var(--muted);
  margin-top: 2px;
}
.row-actions {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}
.row-btn {
  font-size: var(--fs-sm);
  color: var(--muted);
  background: none;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  padding: 4px 10px;
  cursor: pointer;
  transition: all var(--t);
}
.row-btn:hover {
  color: var(--text);
  border-color: var(--line-strong);
}
.row-btn--reset {
  padding: 4px 9px;
}
.row-btn--reset:hover {
  color: var(--err);
}
</style>
