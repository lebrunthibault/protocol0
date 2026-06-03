// État du keymapper : charge bindings + catalogue d'actions, et expose les mutations
// (auto-save par binding, style Raycast). La détection de conflit se fait par égalité
// exacte de la chaîne combo (la canonicalisation étant identique partout).
import { computed, ref } from "vue";
import type { Ref } from "vue";
import { api } from "../api/client";
import type { ActionDef, Binding } from "../api/types";

const bindings = ref<Binding[]>([]);
const actions = ref<ActionDef[]>([]);
const loading = ref(false);
const error = ref<string>("");

async function load(): Promise<void> {
  loading.value = true;
  error.value = "";
  try {
    const [b, a] = await Promise.all([api.listShortcuts(), api.getActions()]);
    bindings.value = b;
    actions.value = a;
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e);
  } finally {
    loading.value = false;
  }
}

// Le binding (autre que celui édité) qui occupe déjà cette combo, le cas échéant.
function conflictFor(combo: string, exceptCombo?: string): Binding | undefined {
  return bindings.value.find((b) => b.combo === combo && b.combo !== exceptCombo);
}

// Upsert par combo. Si l'édition change la combo d'un binding existant, on supprime
// l'ancienne pour ne pas laisser de doublon (la clé de persistance est la combo).
async function save(binding: Binding, previousCombo?: string): Promise<void> {
  if (previousCombo && previousCombo !== binding.combo) {
    await api.deleteShortcut(previousCombo);
  }
  bindings.value = await api.addShortcut(binding);
}

async function remove(combo: string): Promise<void> {
  bindings.value = await api.deleteShortcut(combo);
}

// Singleton module-level : un seul état de keymapper partagé par toutes les vues.
// On expose les refs telles quelles (lecture only par convention ; les mutations
// passent par load/save/remove).
export function useShortcuts() {
  return {
    bindings: bindings as Ref<Binding[]>,
    actions: actions as Ref<ActionDef[]>,
    loading,
    error,
    actionCount: computed(() => bindings.value.length),
    load,
    conflictFor,
    save,
    remove,
  };
}
