<script setup lang="ts">
// Documentation écrite à la main de l'API servie par l'agent (sous /api) + /status.
// L'agent est un http.server stdlib (pas de FastAPI/OpenAPI) -> page statique stylée.
interface Endpoint {
  method: string;
  path: string;
  summary: string;
  body?: string;
  returns: string;
}

const endpoints: Endpoint[] = [
  {
    method: "GET",
    path: "/api/shortcuts",
    summary: "List all configured bindings.",
    returns: "Binding[] — [{ combo, action, params }]",
  },
  {
    method: "POST",
    path: "/api/shortcuts/add",
    summary: "Add or replace the binding for a combo (upsert by combo).",
    body: "{ combo, action, params }",
    returns: "Binding[] — the resulting list",
  },
  {
    method: "POST",
    path: "/api/shortcuts/delete",
    summary: "Delete the binding for a combo.",
    body: "{ combo }",
    returns: "Binding[] — the resulting list",
  },
  {
    method: "GET",
    path: "/api/actions",
    summary: "List the assignable actions and their parameters (static catalog).",
    returns: "ActionDef[] — [{ name, label, params, path, method }]",
  },
  {
    method: "GET",
    path: "/api/health",
    summary: "Agent liveness probe.",
    returns: "{ ok: true, version }",
  },
  {
    method: "GET",
    path: "/status",
    summary: "Diagnostic of the Ableton connection (3 states).",
    returns: '{ state: "no_ableton" | "script_inactive" | "ready", script_url? }',
  },
];
</script>

<template>
  <section class="api-docs stack">
    <div class="page-head">
      <h1>API</h1>
      <p>
        The agent serves this local API on <code>http://127.0.0.1:9010</code>. It is for the
        keymapper UI only (localhost, not a public API) — shortcuts are written straight to
        <code>%APPDATA%\Protocol0\shortcuts.json</code>.
      </p>
    </div>

    <div class="note">
      <p>
        The combo string is canonical: modifiers in the order
        <code>ctrl, alt, shift, win</code>, then the key, lowercase, joined by <code>+</code>
        (e.g. <code>ctrl+shift+f5</code>). It is byte-identical to what the agent's keyboard
        listener matches.
      </p>
    </div>

    <div v-for="e in endpoints" :key="e.method + e.path" class="card card--flat endpoint">
      <div class="endpoint-head">
        <span class="endpoint-method" :class="`endpoint-method--${e.method.toLowerCase()}`">
          {{ e.method }}
        </span>
        <code class="endpoint-path">{{ e.path }}</code>
      </div>
      <p class="endpoint-summary">{{ e.summary }}</p>
      <div v-if="e.body" class="endpoint-line">
        <span class="endpoint-label">Body</span>
        <code>{{ e.body }}</code>
      </div>
      <div class="endpoint-line">
        <span class="endpoint-label">Returns</span>
        <code>{{ e.returns }}</code>
      </div>
    </div>
  </section>
</template>

<style scoped>
.endpoint {
  padding: var(--space-4) var(--space-5);
}
.endpoint-head {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}
.endpoint-method {
  font-family: var(--font-mono);
  font-size: var(--fs-xs);
  font-weight: var(--fw-semibold);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  letter-spacing: 0.04em;
}
.endpoint-method--get {
  color: var(--ok);
  background: rgba(95, 208, 138, 0.12);
}
.endpoint-method--post {
  color: var(--accent);
  background: var(--accent-bg);
}
.endpoint-path {
  font-size: var(--fs-base);
}
.endpoint-summary {
  color: var(--text-soft);
  margin-top: var(--space-3);
}
.endpoint-line {
  display: flex;
  gap: var(--space-3);
  align-items: baseline;
  margin-top: var(--space-2);
}
.endpoint-label {
  font-size: var(--fs-xs);
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  min-width: 4em;
}
</style>
