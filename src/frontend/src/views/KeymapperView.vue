<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useShortcuts } from "../composables/useShortcuts";
import type { Binding } from "../api/types";
import SearchBar from "../components/SearchBar.vue";
import ShortcutRow from "../components/ShortcutRow.vue";
import EditDialog from "../components/EditDialog.vue";

const { bindings, loading, error, actionCount, load, remove } = useShortcuts();

const searchText = ref("");
const searchHotkey = ref("");

const dialogOpen = ref(false);
const editing = ref<Binding | null>(null);

onMounted(load);

const filtered = computed<Binding[]>(() => {
  let list = bindings.value as Binding[];
  if (searchHotkey.value) {
    list = list.filter((b) => b.combo === searchHotkey.value);
  }
  const q = searchText.value.trim().toLowerCase();
  if (q) {
    list = list.filter(
      (b) =>
        b.action.toLowerCase().includes(q) ||
        b.combo.toLowerCase().includes(q) ||
        Object.values(b.params).some((v) => v.toLowerCase().includes(q)),
    );
  }
  return list;
});

function openNew() {
  editing.value = null;
  dialogOpen.value = true;
}
function openEdit(b: Binding) {
  editing.value = b;
  dialogOpen.value = true;
}
async function onRemove(b: Binding) {
  await remove(b.combo);
}
</script>

<template>
  <section class="keymapper">
    <div class="page-head keymapper-head">
      <div>
        <h1>Keyboard shortcuts</h1>
        <p>Record a combo, assign an action. Saved to disk instantly — no Ableton required.</p>
      </div>
      <button type="button" class="btn btn-primary" @click="openNew">+ New shortcut</button>
    </div>

    <SearchBar v-model:text="searchText" v-model:hotkey="searchHotkey" />

    <div class="keymapper-meta">
      <span class="badge">{{ actionCount }} defined</span>
    </div>

    <div v-if="error" class="msg msg--err">{{ error }}</div>
    <div v-else-if="loading" class="msg">Loading…</div>
    <div v-else-if="!filtered.length" class="card card--flat keymapper-empty">
      <p class="msg">
        {{ bindings.length ? "No shortcut matches your search." : "No shortcuts yet — add one." }}
      </p>
    </div>
    <div v-else class="card card--flat keymapper-list">
      <ShortcutRow
        v-for="b in filtered"
        :key="b.combo"
        :binding="b"
        @edit="openEdit(b)"
        @remove="onRemove(b)"
      />
    </div>

    <EditDialog
      :open="dialogOpen"
      :binding="editing"
      @close="dialogOpen = false"
      @saved="load"
    />
  </section>
</template>

<style scoped>
.keymapper-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4);
}
.keymapper-meta {
  margin: var(--space-4) 0;
}
.keymapper-list,
.keymapper-empty {
  padding: 0;
}
.keymapper-empty {
  padding: var(--space-6);
  text-align: center;
}
</style>
