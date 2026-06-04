// Keymapper state: loads bindings + action catalog, and exposes the mutations
// (auto-save per binding, Raycast style). Conflict detection is done by exact
// equality of the combo string (canonicalization being identical everywhere).
import { computed, ref } from "vue";
import type { Ref } from "vue";
import { api } from "../api/client";
import type { AbletonShortcut, ActionDef, Binding } from "../api/types";

const bindings = ref<Binding[]>([]);
const actions = ref<ActionDef[]>([]);
const abletonShortcuts = ref<AbletonShortcut[]>([]);
const abletonDocUrl = ref<string>("");
const loading = ref(false);
const error = ref<string>("");

async function load(): Promise<void> {
  loading.value = true;
  error.value = "";
  try {
    const [b, a, ableton] = await Promise.all([
      api.listShortcuts(),
      api.getActions(),
      api.getAbletonShortcuts(),
    ]);
    bindings.value = b;
    actions.value = a;
    abletonShortcuts.value = ableton.shortcuts;
    abletonDocUrl.value = ableton.doc_url;
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e);
  } finally {
    loading.value = false;
  }
}

// The binding (other than the one being edited) that already occupies this combo, if any.
function conflictFor(combo: string, exceptCombo?: string): Binding | undefined {
  return bindings.value.find((b) => b.combo === combo && b.combo !== exceptCombo);
}

// Upsert by combo. If the edit changes the combo of an existing binding, we delete
// the old one to avoid leaving a duplicate (the persistence key is the combo).
async function save(binding: Binding, previousCombo?: string): Promise<void> {
  if (previousCombo && previousCombo !== binding.combo) {
    await api.deleteShortcut(previousCombo);
  }
  bindings.value = await api.addShortcut(binding);
}

async function remove(combo: string): Promise<void> {
  bindings.value = await api.deleteShortcut(combo);
}

// Module-level singleton: a single keymapper state shared by all views.
// We expose the refs as-is (read-only by convention; mutations go through
// load/save/remove).
export function useShortcuts() {
  return {
    bindings: bindings as Ref<Binding[]>,
    actions: actions as Ref<ActionDef[]>,
    abletonShortcuts: abletonShortcuts as Ref<AbletonShortcut[]>,
    abletonDocUrl,
    loading,
    error,
    actionCount: computed(() => bindings.value.length),
    load,
    conflictFor,
    save,
    remove,
  };
}
