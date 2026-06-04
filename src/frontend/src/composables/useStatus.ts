// Poll of /status (the 3 states computed by the agent). Shared between components
// via a module-level singleton: a single interval for the whole app.
import { onMounted, onUnmounted, readonly, ref } from "vue";
import { api } from "../api/client";
import type { AgentState } from "../api/types";

const state = ref<AgentState | "unknown">("unknown");
const scriptUrl = ref<string | undefined>(undefined);

let timer: number | undefined;
let subscribers = 0;

async function poll(): Promise<void> {
  try {
    const s = await api.getStatus();
    state.value = s.state;
    scriptUrl.value = s.script_url;
  } catch {
    // Agent momentarily unavailable: we'll retry on the next tick.
  }
}

export function useStatus() {
  onMounted(() => {
    subscribers += 1;
    if (timer === undefined) {
      void poll();
      timer = window.setInterval(poll, 2000);
    }
  });
  onUnmounted(() => {
    subscribers -= 1;
    if (subscribers <= 0 && timer !== undefined) {
      window.clearInterval(timer);
      timer = undefined;
    }
  });
  return { state: readonly(state), scriptUrl: readonly(scriptUrl) };
}
