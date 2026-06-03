// Client de l'API servie par l'agent (sous /api) + l'endpoint /status.
// Même origine en prod (l'agent sert la SPA et l'API) ; en dev Vite proxifie vers :9010.
import type { ActionDef, Binding, StatusResponse } from "./types";

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

  // Upsert par combo : ajoute, ou remplace le binding de même combo. Renvoie la liste résultante.
  addShortcut(binding: Binding): Promise<Binding[]> {
    return postJson<Binding[]>("/api/shortcuts/add", binding);
  },

  // Supprime le binding d'une combo (reset-ligne / remplacement sur conflit).
  deleteShortcut(combo: string): Promise<Binding[]> {
    return postJson<Binding[]>("/api/shortcuts/delete", { combo });
  },

  getActions(): Promise<ActionDef[]> {
    return getJson<ActionDef[]>("/api/actions");
  },

  getStatus(): Promise<StatusResponse> {
    return getJson<StatusResponse>("/status");
  },
};
