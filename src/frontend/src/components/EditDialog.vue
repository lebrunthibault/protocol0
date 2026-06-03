<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from "vue";
import hotkeys from "hotkeys-js";
import { useComboCapture } from "../composables/useComboCapture";
import { useShortcuts } from "../composables/useShortcuts";
import type { ActionDef, Binding } from "../api/types";
import Kbd from "./Kbd.vue";

// EditDialog : crée un binding (mode "new") ou édite un binding existant.
const props = defineProps<{
  open: boolean;
  binding: Binding | null; // null = création
}>();
const emit = defineEmits<{ close: []; saved: [] }>();

const { actions, conflictFor, save, remove } = useShortcuts();
const capture = useComboCapture();

const previousCombo = ref<string | undefined>(undefined);
const selectedAction = ref<string>("");
const params = ref<Record<string, string>>({});
const livePreview = ref<string>(""); // touches enfoncées (confort visuel uniquement)
const saving = ref(false);
const saveError = ref<string>("");

const currentAction = computed<ActionDef | undefined>(() =>
  actions.value.find((a) => a.name === selectedAction.value),
);

// Conflit : un autre binding occupe déjà la combo capturée.
const conflict = computed(() =>
  capture.combo.value ? conflictFor(capture.combo.value, previousCombo.value) : undefined,
);

// (Ré)initialise le formulaire à l'ouverture.
watch(
  () => props.open,
  (open) => {
    if (!open) {
      teardownLivePreview();
      return;
    }
    saveError.value = "";
    if (props.binding) {
      previousCombo.value = props.binding.combo;
      selectedAction.value = props.binding.action;
      params.value = { ...props.binding.params };
      // pré-remplit la combo affichée sans repasser en "recording"
      capture.clear();
    } else {
      previousCombo.value = undefined;
      selectedAction.value = actions.value[0]?.name ?? "";
      params.value = {};
      capture.clear();
    }
  },
);

const displayedCombo = computed(
  () => capture.combo.value || props.binding?.combo || "",
);

// --- Capture ---
function onCaptureKeydown(e: KeyboardEvent) {
  capture.onKeydown(e);
}
function startRecording() {
  capture.start();
  setupLivePreview();
}

// --- Live preview (hotkeys-js) : purement visuel, n'influe PAS sur la valeur enregistrée. ---
function setupLivePreview() {
  hotkeys("*", { keyup: true }, () => {
    livePreview.value = hotkeys.getPressedKeyString().join(" + ");
  });
}
function teardownLivePreview() {
  hotkeys.unbind("*");
  livePreview.value = "";
}
onBeforeUnmount(teardownLivePreview);

// --- Save / delete ---
async function onSave() {
  const combo = displayedCombo.value;
  if (!combo) {
    saveError.value = "Capture a combo first.";
    return;
  }
  if (!selectedAction.value) {
    saveError.value = "Pick an action.";
    return;
  }
  // Nettoie les params vides.
  const cleanedParams: Record<string, string> = {};
  for (const p of currentAction.value?.params ?? []) {
    const v = (params.value[p.name] ?? "").trim();
    if (v !== "") cleanedParams[p.name] = v;
  }
  saving.value = true;
  saveError.value = "";
  try {
    // Sur conflit, "Replace" : on supprime d'abord le binding en conflit.
    if (conflict.value) {
      await remove(conflict.value.combo);
    }
    await save({ combo, action: selectedAction.value, params: cleanedParams }, previousCombo.value);
    emit("saved");
    emit("close");
  } catch (e) {
    saveError.value = e instanceof Error ? e.message : String(e);
  } finally {
    saving.value = false;
  }
}

async function onDelete() {
  if (!props.binding) return;
  saving.value = true;
  try {
    await remove(props.binding.combo);
    emit("saved");
    emit("close");
  } catch (e) {
    saveError.value = e instanceof Error ? e.message : String(e);
  } finally {
    saving.value = false;
  }
}
</script>

<template>
  <div v-if="open" class="dialog-backdrop" @click.self="emit('close')">
    <div class="dialog card" role="dialog" aria-modal="true">
      <h2 class="dialog-title">{{ binding ? "Edit shortcut" : "New shortcut" }}</h2>

      <div class="field">
        <label class="field-label" for="action">Action</label>
        <select id="action" class="select" v-model="selectedAction">
          <option v-for="a in actions" :key="a.name" :value="a.name">
            {{ a.label }} ({{ a.name }})
          </option>
        </select>
      </div>

      <div v-if="currentAction && currentAction.params.length" class="field">
        <label
          v-for="p in currentAction.params"
          :key="p.name"
          class="field-label dialog-param"
        >
          {{ p.name }}<span v-if="!p.required"> (optional)</span>
          <input class="input" v-model="params[p.name]" :placeholder="p.name" />
        </label>
      </div>

      <div class="field">
        <label class="field-label">Combo</label>
        <span
          class="capture dialog-capture"
          tabindex="0"
          @keydown="onCaptureKeydown"
          @focus="startRecording"
        >
          <Kbd v-if="displayedCombo" :combo="displayedCombo" />
          <span v-else class="dialog-capture-hint">click &amp; press…</span>
        </span>
        <span v-if="livePreview" class="dialog-live">pressed: {{ livePreview }}</span>
        <span v-if="capture.status.value === 'unsupported'" class="msg msg--err">
          Unsupported key — use letters, digits or F1–F12.
        </span>
      </div>

      <div v-if="conflict" class="warn dialog-conflict">
        <p>
          ⚠ Already used by <strong>{{ conflict.action }}</strong> ({{ conflict.combo }}).
          Saving will <strong>replace</strong> it.
        </p>
      </div>

      <div v-if="saveError" class="msg msg--err">{{ saveError }}</div>

      <div class="dialog-actions">
        <button
          v-if="binding"
          type="button"
          class="btn btn-ghost dialog-delete"
          :disabled="saving"
          @click="onDelete"
        >
          Delete
        </button>
        <span class="dialog-spacer"></span>
        <button type="button" class="btn btn-ghost" :disabled="saving" @click="emit('close')">
          Cancel
        </button>
        <button type="button" class="btn btn-primary" :disabled="saving" @click="onSave">
          {{ conflict ? "Replace" : "Save" }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dialog-backdrop {
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
.dialog {
  width: 100%;
  max-width: 480px;
}
.dialog-title {
  font-size: var(--fs-xl);
  font-weight: var(--fw-semibold);
  text-align: left;
  margin-bottom: var(--space-4);
}
.dialog-param {
  margin-top: var(--space-3);
}
.dialog-capture {
  min-width: 12em;
}
.dialog-capture-hint {
  color: var(--muted-2);
}
.dialog-live {
  display: block;
  margin-top: var(--space-2);
  font-family: var(--font-mono);
  font-size: var(--fs-xs);
  color: var(--muted-2);
}
.dialog-conflict {
  margin: var(--space-4) 0 0;
}
.dialog-actions {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-top: var(--space-5);
}
.dialog-spacer {
  flex: 1;
}
.dialog-delete {
  color: var(--err);
}
</style>
