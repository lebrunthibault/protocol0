<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useComboCapture } from "../composables/useComboCapture";
import { useShortcuts } from "../composables/useShortcuts";
import { SEND_KEYS_ACTION, type Binding, type EditTarget } from "../api/types";
import Kbd from "./Kbd.vue";

// EditDialog assigns/edits a trigger combo for ONE target already chosen in the unified
// list (KeymapperView). The target is either an existing binding (edit: pre-filled, with
// Delete) or a not-yet-mapped catalog entry — a native Ableton shortcut or a smart action.
// The catalog itself lives in the list, not here.
const props = defineProps<{ target: EditTarget }>();
const emit = defineEmits<{ close: []; saved: [] }>();

const { actions, conflictFor, nativePeers, save, remove } = useShortcuts();
const capture = useComboCapture();

const open = computed(() => props.target != null);
const isEdit = computed(() => props.target?.kind === "binding");

// The binding being edited, if any (its previous combo is the persistence key to replace).
const editedBinding = computed<Binding | null>(() =>
  props.target?.kind === "binding" ? props.target.binding : null,
);

// load_device exposes a single editable param ("name"); we surface it first, above the
// trigger combo. Generic over the action's params so a future smart action just works.
const smartParams = ref<Record<string, string>>({});
const previousCombo = ref<string | undefined>(undefined);
const saving = ref(false);
const saveError = ref<string>("");

// The action + the params baseline come straight from the target — no picking needed here.
const resolved = computed<{ action: string; baseParams: Record<string, string> } | null>(
  () => {
    const t = props.target;
    if (!t) return null;
    if (t.kind === "binding")
      return { action: t.binding.action, baseParams: { ...t.binding.params } };
    if (t.kind === "ableton")
      return {
        action: SEND_KEYS_ACTION,
        baseParams: { keys: t.shortcut.keys, label: t.shortcut.label },
      };
    return { action: t.action.name, baseParams: {} };
  },
);

// The smart action definition (load_device…) when the target is a smart one, edit or create.
const smartAction = computed(() => {
  const t = props.target;
  if (!t) return undefined;
  if (t.kind === "smart") return t.action;
  if (t.kind === "binding" && t.binding.action !== SEND_KEYS_ACTION)
    return actions.value.find((a) => a.name === t.binding.action);
  return undefined;
});

// Map a param's declared type (str/int/float/bool, from the script's @action signature)
// to an HTML input. Numbers get a number field (int steps by 1, float by any); bools get a
// checkbox; everything else is free text. Unknown types fall back to text.
function inputKind(type: string): "text" | "number" | "checkbox" {
  if (type === "int" || type === "float" || type === "number" || type === "integer")
    return "number";
  if (type === "bool" || type === "boolean") return "checkbox";
  return "text";
}
function numberStep(type: string): string {
  return type === "int" || type === "integer" ? "1" : "any";
}
// Params persist as strings (Binding.params is Record<string,string>). A checkbox maps to
// "true"/"false"; reading back a stored value treats "true"/"1" as checked.
function paramChecked(name: string): boolean {
  const v = smartParams.value[name];
  return v === "true" || v === "1";
}
function setParamChecked(name: string, checked: boolean): void {
  smartParams.value[name] = checked ? "true" : "false";
}

// Readable header label for the target (native label for an Ableton shortcut, action label
// otherwise). Used in the summary line at the top of the modal.
function targetLabel(): string {
  const t = props.target;
  if (!t) return "";
  if (t.kind === "ableton") return t.shortcut.label;
  if (t.kind === "smart") return t.action.label;
  if (t.binding.action === SEND_KEYS_ACTION)
    return t.binding.params.label || t.binding.params.keys || t.binding.action;
  return smartAction.value?.label ?? t.binding.action;
}
// The action's description (its @action summary), shown under the title as a hint.
const actionDescription = computed<string>(() => smartAction.value?.description ?? "");

// The emitted Ableton combo to show as "emits <Kbd>", if the target is a send_keys one.
const emittedKeys = computed<string>(() => {
  const t = props.target;
  if (!t) return "";
  if (t.kind === "ableton") return t.shortcut.keys;
  if (t.kind === "binding" && t.binding.action === SEND_KEYS_ACTION)
    return t.binding.params.keys;
  return "";
});

// Native-combo sharing: when this target emits a combo that several catalog entries also emit
// (Live reuses e.g. ctrl+i / ctrl+g per context), mapping it de-facto maps them too. Informational,
// not blocking. Exclude the current target's own catalog name so it isn't listed against itself.
const ownShortcutName = computed<string | undefined>(() => {
  const t = props.target;
  if (t?.kind === "ableton") return t.shortcut.name;
  return undefined;
});
const sharedPeers = computed(() =>
  emittedKeys.value ? nativePeers(emittedKeys.value, ownShortcutName.value) : [],
);
const sharedPeersLabel = computed(() =>
  sharedPeers.value.map((s) => s.label).join(", "),
);

// Conflict: another binding already occupies the captured combo.
function bindingLabel(b: Binding): string {
  if (b.action === SEND_KEYS_ACTION) return b.params.label || b.params.keys || b.action;
  return b.action;
}
const conflict = computed(() =>
  capture.combo.value ? conflictFor(capture.combo.value, previousCombo.value) : undefined,
);
const conflictLabel = computed(() => (conflict.value ? bindingLabel(conflict.value) : ""));

// (Re)initialise the form when a target is set (modal opens).
watch(
  () => props.target,
  (t) => {
    if (!t) return;
    saveError.value = "";
    capture.clear();
    if (t.kind === "binding") {
      previousCombo.value = t.binding.combo;
      smartParams.value = { ...t.binding.params };
    } else {
      previousCombo.value = undefined;
      smartParams.value = {};
    }
    // Autofocus the capture zone so the combo can be typed immediately (after it renders).
    nextTick(() => captureEl.value?.focus());
  },
  { immediate: true },
);

const displayedCombo = computed(
  () => capture.combo.value || editedBinding.value?.combo || "",
);

// --- Trigger combo capture ---
// The capture zone, focused on open so the user can type a combo straight away (focusing it
// fires @focus -> startRecording).
const captureEl = ref<HTMLElement | null>(null);
function onCaptureKeydown(e: KeyboardEvent) {
  capture.onKeydown(e);
}
function startRecording() {
  capture.start();
}

// Browser-reserved shortcuts (Ctrl+N/T/W) never fire a capturable keydown in a tab, so we
// offer them through a small dropdown to still be able to assign them.
const RESERVED_COMBOS = ["ctrl+n", "ctrl+t", "ctrl+w"];
const reservedMenuOpen = ref(false);
const reservedWrap = ref<HTMLElement | null>(null);

function pickReserved(combo: string) {
  capture.set(combo);
  reservedMenuOpen.value = false;
}
function onReservedDocClick(e: MouseEvent) {
  if (reservedWrap.value && !reservedWrap.value.contains(e.target as Node)) {
    reservedMenuOpen.value = false;
  }
}

// --- Save / delete ---
async function onSave() {
  const combo = displayedCombo.value;
  if (!combo) {
    saveError.value = "Capture a combo first.";
    return;
  }
  const base = resolved.value;
  if (!base) return;

  const action = base.action;
  const cleanedParams: Record<string, string> = { ...base.baseParams };
  // For smart actions, take the editable param values. A bool always has a value
  // ("true"/"false") so it's kept as-is; text/number params are trimmed and dropped if empty.
  for (const p of smartAction.value?.params ?? []) {
    if (inputKind(p.type) === "checkbox") {
      cleanedParams[p.name] = paramChecked(p.name) ? "true" : "false";
      continue;
    }
    const v = (smartParams.value[p.name] ?? "").trim();
    if (v !== "") cleanedParams[p.name] = v;
    else delete cleanedParams[p.name];
  }

  saving.value = true;
  saveError.value = "";
  try {
    if (conflict.value) {
      await remove(conflict.value.combo);
    }
    await save({ combo, action, params: cleanedParams }, previousCombo.value);
    emit("saved");
    emit("close");
  } catch (e) {
    saveError.value = e instanceof Error ? e.message : String(e);
  } finally {
    saving.value = false;
  }
}

async function onDelete() {
  const b = editedBinding.value;
  if (!b) return;
  saving.value = true;
  try {
    await remove(b.combo);
    emit("saved");
    emit("close");
  } catch (e) {
    saveError.value = e instanceof Error ? e.message : String(e);
  } finally {
    saving.value = false;
  }
}

// Esc closes the reserved menu if open, else the modal. When a capture zone has focus its
// onKeydown stopPropagation-s (Esc becomes an assignable key) so this handler won't see it.
function onKey(e: KeyboardEvent) {
  if (e.key !== "Escape" || !open.value) return;
  if (reservedMenuOpen.value) {
    reservedMenuOpen.value = false;
    return;
  }
  emit("close");
}
onMounted(() => {
  document.addEventListener("keydown", onKey);
  document.addEventListener("click", onReservedDocClick);
});
onBeforeUnmount(() => {
  document.removeEventListener("keydown", onKey);
  document.removeEventListener("click", onReservedDocClick);
});
</script>

<template>
  <div v-if="open && target" class="dialog-backdrop" @click.self="emit('close')">
    <div class="dialog card" role="dialog" aria-modal="true">
      <h2 class="dialog-title">{{ isEdit ? "Edit shortcut" : "Add shortcut" }}</h2>

      <!-- Target summary: what this combo will trigger. -->
      <div class="field">
        <div class="edit-summary">
          <span class="edit-summary-label">{{ targetLabel() }}</span>
          <span v-if="emittedKeys" class="edit-summary-emits">
            emits <Kbd :combo="emittedKeys" />
          </span>
        </div>
        <p v-if="actionDescription" class="edit-summary-desc">{{ actionDescription }}</p>
        <!-- Native-combo sharing: Live reuses this keystroke across contexts, so mapping it also
             drives the listed commands (same injected keys). Informational, not blocking. -->
        <p v-if="sharedPeers.length" class="edit-summary-shared">
          <span class="edit-summary-shared-icon" aria-hidden="true">⚠</span>
          This native combo is also: <strong>{{ sharedPeersLabel }}</strong> — mapping it drives
          those too (Live reuses the keystroke per context).
        </p>
      </div>

      <!-- Smart action params first (e.g. load_device's name). Input type follows the
           param's declared type: number for int/float, checkbox for bool, text otherwise. -->
      <div v-if="smartAction && smartAction.params.length" class="field">
        <label
          v-for="p in smartAction.params"
          :key="p.name"
          class="field-label dialog-param"
          :class="{ 'dialog-param-bool': inputKind(p.type) === 'checkbox' }"
        >
          {{ p.name }}<span v-if="!p.required"> (optional)</span>
          <input
            v-if="inputKind(p.type) === 'checkbox'"
            type="checkbox"
            :checked="paramChecked(p.name)"
            @change="setParamChecked(p.name, ($event.target as HTMLInputElement).checked)"
          />
          <input
            v-else-if="inputKind(p.type) === 'number'"
            class="input"
            type="number"
            :step="numberStep(p.type)"
            v-model="smartParams[p.name]"
            :placeholder="p.name"
          />
          <input v-else class="input" v-model="smartParams[p.name]" :placeholder="p.name" />
        </label>
      </div>

      <div class="field trigger-field">
        <span class="field-label trigger-label">Trigger combo</span>
        <div class="trigger-row">
          <span
            ref="captureEl"
            class="capture dialog-capture"
            tabindex="0"
            @keydown="onCaptureKeydown"
            @focus="startRecording"
          >
            <Kbd v-if="displayedCombo" :combo="displayedCombo" />
          </span>
          <!-- Browser-reserved shortcuts (Ctrl+N/T/W): not capturable, picked here. -->
          <div ref="reservedWrap" class="reserved">
            <button
              type="button"
              class="reserved-btn"
              tabindex="-1"
              title="Reserved shortcuts — the browser blocks these, pick one here"
              aria-label="Reserved shortcuts"
              @click="reservedMenuOpen = !reservedMenuOpen"
            >
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                aria-hidden="true"
              >
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="16" x2="12" y2="12" />
                <line x1="12" y1="8" x2="12.01" y2="8" />
              </svg>
            </button>
            <div v-if="reservedMenuOpen" class="reserved-menu" role="menu">
              <button
                v-for="rc in RESERVED_COMBOS"
                :key="rc"
                type="button"
                class="reserved-item"
                role="menuitem"
                tabindex="-1"
                @click="pickReserved(rc)"
              >
                <Kbd :combo="rc" />
              </button>
            </div>
          </div>
          <!-- Conflict warning in the free space on the right (keeps the modal from growing). -->
          <span
            v-if="conflict"
            class="trigger-warn"
            :title="`Already used by ${conflictLabel} (${conflict.combo}). Saving will replace it.`"
          >
            <span class="trigger-warn-icon" aria-hidden="true">⚠</span>
            Already used by <strong>{{ conflictLabel }}</strong> — saving replaces it.
          </span>
        </div>
        <span v-if="capture.status.value === 'unsupported'" class="msg msg--err">
          Unsupported key — use letters, digits, F1–F12, punctuation like , [ ] = -,
          or keys like Space, Tab, Enter, Esc, arrows.
        </span>
      </div>

      <div v-if="saveError" class="msg msg--err">{{ saveError }}</div>

      <div class="dialog-actions">
        <button
          v-if="isEdit"
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
  max-width: 560px;
  max-height: calc(100vh - 2 * var(--space-6));
  overflow-y: auto;
}
.dialog :deep(.field) {
  margin-bottom: var(--space-4);
}
.dialog-title {
  font-size: var(--fs-2xl);
  font-weight: 600;
  text-align: left;
  margin-bottom: var(--space-5);
}
.dialog-param {
  margin-top: var(--space-3);
}
/* Target summary */
.edit-summary {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: var(--panel-2);
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
}
.edit-summary-label {
  font-size: var(--fs-base);
}
.edit-summary-desc {
  margin: var(--space-2) 0 0;
  font-size: var(--fs-xs);
  color: var(--muted);
}
.edit-summary-emits {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  margin-left: auto;
  font-size: var(--fs-xs);
  color: var(--muted);
}
/* Native-combo sharing note (distinct from the trigger conflict warning further down). */
.edit-summary-shared {
  margin: var(--space-2) 0 0;
  font-size: var(--fs-xs);
  color: var(--warn);
  line-height: 1.4;
}
.edit-summary-shared-icon {
  margin-right: var(--space-1);
}
.edit-summary-shared strong {
  font-weight: 600;
}
.trigger-field {
  margin-top: var(--space-5);
}
.trigger-label {
  display: block;
  margin-bottom: var(--space-3);
}
/* Capture field + warning side by side. */
.trigger-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}
.dialog-capture {
  /* Comfortable width + stable height even when empty (otherwise the field
     shrinks to its padding until a combo is captured). */
  flex: none;
  width: 16em;
  min-height: 42px;
  display: inline-flex;
  align-items: center;
}
/* Reserved shortcuts menu (Ctrl+N/T/W). */
.reserved {
  position: relative;
  flex: none;
}
.reserved-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  padding: 0;
  border: none;
  background: transparent;
  color: var(--muted);
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: color var(--t), background var(--t);
}
.reserved-btn:hover {
  color: var(--text);
  background: rgba(255, 255, 255, 0.06);
}
.reserved-btn svg {
  width: 16px;
  height: 16px;
}
.reserved-menu {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  z-index: 10;
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: var(--space-2);
  background: var(--panel);
  border: 1px solid var(--line-strong);
  border-radius: var(--radius-md);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
}
.reserved-item {
  display: flex;
  align-items: center;
  padding: var(--space-2);
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: background var(--t);
}
.reserved-item:hover {
  background: var(--accent-bg);
}
/* Conflict warning, in the free space on the right (keeps the modal from growing). */
.trigger-warn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  min-width: 0;
  font-size: var(--fs-xs);
  color: var(--warn);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.trigger-warn strong {
  font-weight: 600;
}
.trigger-warn-icon {
  flex: none;
  font-size: var(--fs-base);
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
