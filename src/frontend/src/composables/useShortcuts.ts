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

// Native-combo sharing (orthogonal to conflictFor, which is about TRIGGER combos): several
// catalog entries can emit the SAME native combo (Live reuses e.g. ctrl+i, ctrl+g per context).
// Mapping a trigger to one of them de-facto maps them all, since it's the same injected keystroke.
// Derived purely from the catalog, grouped by `keys`.
const sharedByKeys = computed(() => {
  const m = new Map<string, AbletonShortcut[]>();
  for (const s of abletonShortcuts.value) {
    const arr = m.get(s.keys);
    if (arr) arr.push(s);
    else m.set(s.keys, [s]);
  }
  // Keep only the genuinely-shared combos (2+ entries).
  for (const [k, arr] of m) if (arr.length < 2) m.delete(k);
  return m;
});

// The OTHER catalog entries sharing a native combo (excluding the one named, if given).
function nativePeers(keys: string, exceptName?: string): AbletonShortcut[] {
  const arr = sharedByKeys.value.get(keys);
  if (!arr) return [];
  return exceptName ? arr.filter((s) => s.name !== exceptName) : arr;
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
    sharedByKeys,
    nativePeers,
    save,
    remove,
  };
}
