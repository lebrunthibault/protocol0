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

// Classe de couleur du point (ok / warn / muted).
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

const title = computed(() =>
  state.value === "ready"
    ? "Le script Protocol 0 est joignable : les raccourcis déclenchent des actions."
    : "Vous pouvez éditer vos raccourcis ; lancez Ableton (et activez le remote script) pour les déclencher.",
);
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
