// Client for the API served by the agent (under /api) + the /status endpoint.
// Same origin in prod (the agent serves the SPA and the API); in dev Vite proxies to :9010.
import type { AbletonShortcutCatalog, ActionDef, Binding, StatusResponse } from "./types";

async function getJson<T>(url: string): Promise<T> {
  const r = await fetch(url, { headers: { Accept: "application/json" } });
  if (!r.ok) throw new Error(`${url} -> HTTP ${r.status}`);
  return (await r.json()) as T;
}

async function postJson<T>(url: string, body: unknown): Promise<T> {
  const r = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`${url} -> HTTP ${r.status}: ${await r.text()}`);
  return (await r.json()) as T;
}

export const api = {
  listShortcuts(): Promise<Binding[]> {
    return getJson<Binding[]>("/api/shortcuts");
  },

  // Upsert by combo: adds, or replaces the binding with the same combo. Returns the resulting list.
  addShortcut(binding: Binding): Promise<Binding[]> {
    return postJson<Binding[]>("/api/shortcuts/add", binding);
  },

  // Deletes the binding of a combo (row reset / replacement on conflict).
  deleteShortcut(combo: string): Promise<Binding[]> {
    return postJson<Binding[]>("/api/shortcuts/delete", { combo });
  },

  getActions(): Promise<ActionDef[]> {
    return getJson<ActionDef[]>("/api/actions");
  },

  // Curated native Live shortcuts offered as remap targets (send_keys).
  getAbletonShortcuts(): Promise<AbletonShortcutCatalog> {
    return getJson<AbletonShortcutCatalog>("/api/ableton-shortcuts");
  },

  getStatus(): Promise<StatusResponse> {
    return getJson<StatusResponse>("/status");
  },
};
