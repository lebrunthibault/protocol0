<script setup lang="ts">
// Documentation de l'API du script Protocol 0 (les routes exposées DANS Ableton).
// Statique : le script tourne sur un port dynamique et meurt avec Ableton, donc on
// documente ses routes en dur ici plutôt que de les fetch (la page s'affiche même
// Ableton fermé). À garder en phase avec src/script/.../http/routes/*.
//
// L'API du script est une vraie API REST sous /api : GET en lecture, POST (body
// JSON) en mutation. La version live + interactive est servie par le script
// lui-même en Swagger UI sur /docs (et /openapi.json) quand Ableton tourne.
interface Param {
  name: string;
  type: string;
  required: boolean;
}
interface Endpoint {
  method: string;
  path: string;
  summary: string;
  params: Param[];
  returns: string;
}

const endpoints: Endpoint[] = [
  {
    method: "POST",
    path: "/api/device/load",
    summary: "Load a device (instrument or audio effect) onto the selected track by name.",
    params: [{ name: "name", type: "str", required: true }],
    returns: "200 — fire-and-forget",
  },
  {
    method: "POST",
    path: "/api/track/select",
    summary: 'Select a track by name (use "master" to select the master track).',
    params: [{ name: "name", type: "str", required: true }],
    returns: "200 — fire-and-forget",
  },
  {
    method: "POST",
    path: "/api/song/toggle_follow",
    summary: "Stop following the playhead in the arrangement view.",
    params: [],
    returns: "200 — fire-and-forget",
  },
  {
    method: "POST",
    path: "/api/clip/key_detected",
    summary: "Notify the script that a musical key (MIDI pitch) was detected for the current clip.",
    params: [{ name: "pitch", type: "int", required: true }],
    returns: "200 — fire-and-forget",
  },
  {
    method: "GET",
    path: "/api/set/get_state",
    summary: "Return the full serialized state of the current Ableton set.",
    params: [],
    returns: "AbletonSet — JSON",
  },
  {
    method: "GET",
    path: "/api/health",
    summary: "Liveness probe.",
    params: [],
    returns: "{ ok: true, version }",
  },
];

function paramSignature(params: Param[]): string {
  if (!params.length) return "—";
  return params
    .map((p) => `${p.name}: ${p.type}${p.required ? "" : "?"}`)
    .join(", ");
}
</script>

<template>
  <section class="api-docs stack">
    <div class="page-head">
      <h1>Script API</h1>
      <p>
        These are the actions the Protocol&nbsp;0 remote script exposes <strong>inside
        Ableton</strong>. The agent calls them when you trigger a shortcut. They are also
        the building blocks you can bind to in the
        <RouterLink to="/shortcuts">keymapper</RouterLink>.
      </p>
    </div>

    <div class="note">
      <p>
        The script serves this API on a <strong>dynamic local port</strong> (it lives and dies
        with Ableton; the agent discovers its URL via
        <code>%APPDATA%\Protocol0\runtime.json</code>). It's a REST API under <code>/api</code>:
        reads are <code>GET</code>, mutations are <code>POST</code> with a JSON body. A live,
        interactive Swagger UI is served by the script itself at <code>/docs</code> (and the
        spec at <code>/openapi.json</code>) when Ableton is running.
      </p>
    </div>

    <div v-for="e in endpoints" :key="e.method + e.path" class="card card--flat endpoint">
      <div class="endpoint-head">
        <span
          class="endpoint-method"
          :class="e.method === 'GET' ? 'endpoint-method--get' : 'endpoint-method--post'"
        >{{ e.method }}</span>
        <code class="endpoint-path">{{ e.path }}</code>
      </div>
      <p class="endpoint-summary">{{ e.summary }}</p>
      <div class="endpoint-line">
        <span class="endpoint-label">Params</span>
        <code>{{ paramSignature(e.params) }}</code>
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
  color: var(--accent-blue, #5aa9ff);
  background: rgba(90, 169, 255, 0.12);
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
