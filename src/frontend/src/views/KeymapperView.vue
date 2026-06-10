<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useShortcuts } from "../composables/useShortcuts";
import { useStatus } from "../composables/useStatus";
import { SEND_KEYS_ACTION, type ActionDef, type Binding, type EditTarget } from "../api/types";
import SearchBar from "../components/SearchBar.vue";
import EditDialog from "../components/EditDialog.vue";
import GateOverlay from "../components/GateOverlay.vue";
import Kbd from "../components/Kbd.vue";

const {
  bindings,
  actions,
  abletonShortcuts,
  loading,
  error,
  actionCount,
  abletonDocUrl,
  nativePeers,
  load,
} = useShortcuts();

// Editing only makes sense when Ableton is connected and the remote script is live.
// Any other state locks the UI behind a blocking GateOverlay.
const { state } = useStatus();
const locked = computed(() => state.value !== "ready");

const searchText = ref("");
const searchHotkey = ref("");

// Filter pills: All (default) -> Ableton shortcuts -> Smart actions.
type Filter = "all" | "ableton" | "smart";
const filter = ref<Filter>("all");
const mappedOnly = ref(false);

// The target handed to the modal (an existing binding, or a catalog entry to map). null = closed.
const target = ref<EditTarget>(null);

// If the connection drops mid-edit, close the open dialog so the gate can take over.
watch(locked, (isLocked) => {
  if (isLocked) target.value = null;
});

onMounted(load);

// One row of the unified list. An Ableton row carries its catalog entry + the binding that
// maps it, if any. A smart row is either an existing load_device binding or the "new mapping"
// template (no binding yet).
interface AbletonRow {
  kind: "ableton";
  key: string;
  label: string;
  combo: string; // trigger combo if mapped, else ""
  shortcut: (typeof abletonShortcuts.value)[number];
  binding: Binding | null;
  peers: string[]; // other catalog labels sharing this native combo (empty if none)
}
interface SmartRow {
  kind: "smart";
  key: string;
  label: string;
  combo: string;
  action: ActionDef;
  binding: Binding | null; // null = "new mapping" template
}
type Row = AbletonRow | SmartRow;
interface Group {
  category: string;
  rows: Row[];
}

// Index the user's bindings: send_keys keyed by the emitted Ableton combo, smart ones split out.
const sendKeysByCombo = computed(() => {
  const m = new Map<string, Binding>();
  for (const b of bindings.value) {
    if (b.action === SEND_KEYS_ACTION) m.set(b.params.keys, b);
  }
  return m;
});
const smartBindings = computed(() =>
  bindings.value.filter((b) => b.action !== SEND_KEYS_ACTION),
);

function matchesSearch(label: string, combo: string, keys: string): boolean {
  const h = searchHotkey.value.trim().toLowerCase();
  if (h && !combo.toLowerCase().includes(h) && !keys.toLowerCase().includes(h)) return false;
  const q = searchText.value.trim().toLowerCase();
  if (q && !`${label} ${combo} ${keys}`.toLowerCase().includes(q)) return false;
  return true;
}

// "load_device" -> "Load Device" (underscores to spaces, then title-case every word).
function humanizeAction(name: string): string {
  return name
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

// A binding's param values appended to its action name, e.g. "Load Device: Reverb".
// Generic over any action — joins the (non-empty) param values the binding carries.
function bindingLabel(b: Binding): string {
  const values = Object.values(b.params).filter((v) => v !== "");
  const base = humanizeAction(b.action);
  return values.length ? `${base}: ${values.join(", ")}` : base;
}

// Ableton groups: the catalog grouped by category, in catalog order, each entry annotated
// with the binding that maps it (if any). Filtered by search + mapped-only.
const abletonGroups = computed<Group[]>(() => {
  if (filter.value === "smart") return [];
  const groups: Group[] = [];
  const byCat = new Map<string, Row[]>();
  for (const s of abletonShortcuts.value) {
    const binding = sendKeysByCombo.value.get(s.keys) ?? null;
    if (mappedOnly.value && !binding) continue;
    if (!matchesSearch(s.label, binding?.combo ?? "", s.keys)) continue;
    let rows = byCat.get(s.category);
    if (!rows) {
      rows = [];
      byCat.set(s.category, rows);
      groups.push({ category: s.category, rows });
    }
    rows.push({
      kind: "ableton",
      key: s.name,
      label: s.label,
      combo: binding?.combo ?? "",
      shortcut: s,
      binding,
      peers: nativePeers(s.keys, s.name).map((p) => p.label),
    });
  }
  return groups;
});

// Smart actions group: for every catalog action, a "<Action> — new mapping" template,
// then one row per existing binding of that action. Generic over the whole catalog (drop
// a plugin @action in the script and it shows up here). Filtered by search + mapped-only.
const smartGroup = computed<Group | null>(() => {
  if (filter.value === "ableton") return null;
  const rows: Row[] = [];
  for (const action of actions.value) {
    if (!mappedOnly.value && matchesSearch(humanizeAction(action.name), "", "")) {
      rows.push({
        kind: "smart",
        key: `${action.name}:new`,
        label: `${humanizeAction(action.name)} — new mapping`,
        combo: "",
        action,
        binding: null,
      });
    }
    for (const b of smartBindings.value) {
      if (b.action !== action.name) continue;
      const label = bindingLabel(b);
      if (!matchesSearch(label, b.combo, "")) continue;
      rows.push({ kind: "smart", key: `b:${b.combo}`, label, combo: b.combo, action, binding: b });
    }
  }
  if (!rows.length) return null;
  return { category: "Smart actions", rows };
});

const groups = computed<Group[]>(() => {
  const g = [...abletonGroups.value];
  if (smartGroup.value) g.push(smartGroup.value);
  return g;
});

const hasRows = computed(() => groups.value.some((g) => g.rows.length));

// Folded categories. All collapsed by default; an active search/filter auto-expands groups
// that have results (to reveal them).
const expanded = ref<Set<string>>(new Set());
const searchActive = computed(
  () => searchText.value.trim() !== "" || searchHotkey.value.trim() !== "" || mappedOnly.value,
);
const isExpanded = (category: string) => searchActive.value || expanded.value.has(category);
function toggleCategory(category: string) {
  const next = new Set(expanded.value);
  if (next.has(category)) next.delete(category);
  else next.add(category);
  expanded.value = next;
}

// Click a row -> open the modal on the right target.
function openRow(row: Row) {
  if (row.binding) {
    target.value = { kind: "binding", binding: row.binding };
  } else if (row.kind === "ableton") {
    target.value = { kind: "ableton", shortcut: row.shortcut };
  } else {
    target.value = { kind: "smart", action: row.action };
  }
}
</script>

<template>
  <section class="keymapper">
    <div class="page-head keymapper-head">
      <h1>Keyboard shortcuts</h1>
      <p>
        Pick an action below and record a combo to remap it to a native
        <a
          v-if="abletonDocUrl"
          class="doc-link-soft"
          :href="abletonDocUrl"
          target="_blank"
          rel="noopener"
          title="See the official Ableton shortcut reference"
        >Ableton shortcut</a>
        <template v-else>Ableton shortcut</template>
        or a smart action.
      </p>
    </div>

    <div class="keymapper-body" :class="{ 'is-locked': locked }">
      <div class="keymapper-controls">
        <SearchBar v-model:text="searchText" v-model:hotkey="searchHotkey" />
      </div>

    <div class="keymapper-bar">
      <div class="mode-tabs" role="tablist">
        <button
          type="button"
          class="mode-tab"
          :class="{ 'mode-tab--on': filter === 'all' }"
          role="tab"
          :aria-selected="filter === 'all'"
          @click="filter = 'all'"
        >
          All
        </button>
        <button
          type="button"
          class="mode-tab"
          :class="{ 'mode-tab--on': filter === 'ableton' }"
          role="tab"
          :aria-selected="filter === 'ableton'"
          @click="filter = 'ableton'"
        >
          Ableton shortcuts
        </button>
        <button
          type="button"
          class="mode-tab"
          :class="{ 'mode-tab--on': filter === 'smart' }"
          role="tab"
          :aria-selected="filter === 'smart'"
          @click="filter = 'smart'"
        >
          Smart actions
        </button>
      </div>
      <label class="mapped-toggle">
        <input type="checkbox" v-model="mappedOnly" />
        Show mapped only
      </label>
      <span class="badge keymapper-count">{{ actionCount }} mapped</span>
    </div>

    <div v-if="error" class="msg msg--err">{{ error }}</div>
    <div v-else-if="loading" class="msg">Loading…</div>
    <div v-else-if="!hasRows" class="card card--flat keymapper-empty">
      <p class="msg">
        {{ mappedOnly ? "No shortcut mapped yet." : "No shortcut matches your search." }}
      </p>
    </div>
    <div v-else class="card card--flat ableton-list keymapper-list">
      <div v-for="g in groups" :key="g.category" class="ableton-group">
        <button
          type="button"
          class="ableton-group-head"
          :aria-expanded="isExpanded(g.category)"
          @click="toggleCategory(g.category)"
        >
          <span class="ableton-caret" :class="{ 'ableton-caret--open': isExpanded(g.category) }">▸</span>
          <span class="ableton-group-name">{{ g.category }}</span>
          <span class="ableton-group-count">{{ g.rows.length }}</span>
        </button>
        <div v-if="isExpanded(g.category)" class="ableton-group-body">
          <button
            v-for="row in g.rows"
            :key="row.key"
            type="button"
            class="ableton-item"
            :class="{ 'ableton-item--new': !row.binding && row.kind === 'smart' }"
            @click="openRow(row)"
          >
            <span class="ableton-item-label">{{ row.label }}</span>
            <!-- Shared native combo: this keystroke also drives other commands. Shown on every
                 shared row; emphasised once mapped (mapping it moved those peers too). -->
            <span
              v-if="row.kind === 'ableton' && row.peers.length"
              class="ableton-shared-badge"
              :class="{ 'ableton-shared-badge--mapped': row.binding }"
              :title="`Same native combo as: ${row.peers.join(', ')}${row.binding ? ' — these were mapped together' : ''}`"
            >⚠ +{{ row.peers.length }}</span>
            <Kbd v-if="row.combo" :combo="row.combo" />
          </button>
        </div>
      </div>
    </div>

    </div>

    <EditDialog :target="target" @close="target = null" @saved="load" />
    <GateOverlay v-if="locked" :state="state" />
  </section>
</template>

<style scoped>
/* When not connected to Ableton, the editable area is blurred and inert behind
   the GateOverlay; pointer-events: none is defence-in-depth so no click lands. */
.keymapper-body.is-locked {
  filter: blur(2px);
  pointer-events: none;
  user-select: none;
}

/* Soft doc link, woven into the description sentence (grey -> visible on hover). */
.doc-link-soft {
  color: var(--muted);
  text-decoration: underline;
  text-decoration-color: var(--line-strong);
  text-underline-offset: 2px;
  transition: color var(--t);
}
.doc-link-soft:hover {
  color: var(--accent-soft);
}
.keymapper-controls {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}
.keymapper-controls :deep(.search) {
  flex: 1;
}
/* Filter pills + mapped-only toggle + count, on one line above the list. */
.keymapper-bar {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  margin: var(--space-4) 0;
}
.mapped-toggle {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--fs-sm);
  color: var(--muted);
  cursor: pointer;
  user-select: none;
}
.mapped-toggle input {
  cursor: pointer;
  accent-color: var(--accent);
}
.keymapper-count {
  margin-left: auto;
}
.keymapper-list {
  max-height: calc(100vh - 320px);
  min-height: 200px;
}
.keymapper-empty {
  padding: var(--space-6);
  text-align: center;
}
/* "New mapping" template row: lighter, italic so it reads as an action, not a binding. */
.ableton-item--new .ableton-item-label {
  color: var(--accent-soft);
  font-style: italic;
}
/* Shared-native-combo badge: muted hint by default, emphasised once the row is mapped.
   margin-left:auto pushes it (and the trailing Kbd) to the right of the row. */
.ableton-shared-badge {
  flex: none;
  margin-left: auto;
  font-size: var(--fs-xs);
  color: var(--muted);
  white-space: nowrap;
}
/* When a Kbd follows the badge, they share the right side: drop the auto-margin off the Kbd
   gap by giving the badge a small right gap instead. */
.ableton-shared-badge + :deep(.kbd-combo) {
  flex: none;
}
.ableton-shared-badge--mapped {
  color: var(--warn);
}
</style>
