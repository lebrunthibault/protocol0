<script setup lang="ts">
// Blocking gate shown over the shortcuts UI whenever the agent is not fully
// connected to Ableton. Editing a shortcut only makes sense when Ableton is
// running AND the remote script is active (state === "ready"); any other state
// raises this overlay, which tells the user what to do. It is intentionally NOT
// dismissible — the only way out is for the status poll to flip back to "ready".
import { computed } from "vue";
import type { AgentState } from "../api/types";

const props = defineProps<{ state: AgentState | "unknown" }>();

const title = computed(() => {
  switch (props.state) {
    case "no_ableton":
      return "Launch Ableton Live";
    case "script_inactive":
      return "Activate the Protocol 0 remote script";
    default:
      return "Connecting…";
  }
});

const body = computed(() => {
  switch (props.state) {
    case "no_ableton":
      return "Open Ableton Live to edit your shortcuts. This page will unlock automatically once it's running.";
    case "script_inactive":
      return 'Add the Protocol 0 remote script to your Control Surface in the "Link, Tempo & MIDI" preferences. The page unlocks as soon as it\'s active.';
    default:
      return "Reaching the Protocol 0 agent…";
  }
});
</script>

<template>
  <div class="gate-backdrop">
    <div class="gate card" role="dialog" aria-modal="true">
      <span class="gate-dot" :class="`gate-dot--${state}`"></span>
      <h2 class="gate-title">{{ title }}</h2>
      <p class="gate-body">{{ body }}</p>
    </div>
  </div>
</template>

<style scoped>
.gate-backdrop {
  position: fixed;
  inset: 0;
  z-index: 100;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-5);
}
.gate {
  width: 100%;
  max-width: 460px;
  text-align: center;
  padding: var(--space-6);
  display: flex;
  flex-direction: column;
  align-items: center;
  user-select: none;
  cursor: default;
}
.gate-dot {
  display: block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-bottom: var(--space-4);
  background: var(--muted-2);
}
.gate-dot--no_ableton {
  background: var(--muted-2);
}
.gate-dot--script_inactive {
  background: var(--warn);
}
.gate-title {
  font-size: var(--fs-2xl);
  font-weight: 600;
  margin-bottom: var(--space-3);
}
.gate-body {
  color: var(--muted);
  font-size: var(--fs-base);
  line-height: 1.5;
}
</style>
