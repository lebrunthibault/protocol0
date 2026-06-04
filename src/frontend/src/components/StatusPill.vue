<script setup lang="ts">
import { computed } from "vue";
import { useStatus } from "../composables/useStatus";

const { state } = useStatus();

const label = computed(() => {
  switch (state.value) {
    case "ready":
      return "Ableton connected";
    case "script_inactive":
      return "Activate the remote script";
    case "no_ableton":
      return "Ableton closed";
    default:
      return "Checking…";
  }
});

// Color class of the dot (ok / warn / muted).
const tone = computed(() => {
  switch (state.value) {
    case "ready":
      return "ok";
    case "script_inactive":
      return "warn";
    default:
      return "muted";
  }
});

const title = computed(() => {
  switch (state.value) {
    case "ready":
      return "The Protocol 0 script is reachable: shortcuts trigger actions.";
    case "script_inactive":
      return 'Please add the Protocol0 remote script to your Control Surface in the "Tempo & Midi" Preferences Section';
    default:
      return "Launch Ableton and activate the remote script to edit and trigger your shortcuts.";
  }
});
</script>

<template>
  <span class="status-pill" :title="title">
    <span class="status-dot" :class="`status-dot--${tone}`"></span>
    {{ label }}
  </span>
</template>

<style scoped>
.status-pill {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--fs-sm);
  color: var(--muted);
  border: 1px solid var(--line);
  border-radius: var(--radius-pill);
  padding: 5px 12px;
  background: rgba(255, 255, 255, 0.02);
  white-space: nowrap;
}
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex: 0 0 auto;
}
.status-dot--ok {
  background: var(--ok);
  box-shadow: 0 0 8px var(--ok);
}
.status-dot--warn {
  background: var(--warn);
}
.status-dot--muted {
  background: var(--muted-2);
}
</style>
