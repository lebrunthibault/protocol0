// Poll de /status (les 3 états calculés par l'agent). Partagé entre les composants
// via un singleton module-level : un seul interval pour toute l'app.
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
    // Agent momentanément indispo : on retentera au prochain tick.
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
