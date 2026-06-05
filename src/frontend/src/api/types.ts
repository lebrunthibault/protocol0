// Contract shared with the agent (src/agent, Rust). The `shortcuts.json` schema is versioned
// (version 1): a binding = { combo, action, params }. The combo is canonical
// (ctrl, alt, shift, win + key, lowercase, joined by '+') — identical to what
// the agent's listener matches.

export interface Binding {
  combo: string;
  action: string;
  params: Record<string, string>;
}

export interface ActionParam {
  name: string;
  type: string;
  required: boolean;
}

export interface ActionDef {
  name: string;
  label: string; // the action name in Title Case (e.g. "Load Device")
  description: string; // the @action method's summary (first docstring line)
  params: ActionParam[];
  path: string;
  method: string;
}

// A native Ableton Live shortcut, offered as a remap target. `keys` is the canonical
// combo the agent replays when the user's combo fires (action "send_keys").
export interface AbletonShortcut {
  name: string;
  label: string;
  category: string;
  keys: string;
}

export interface AbletonShortcutCatalog {
  doc_url: string;
  shortcuts: AbletonShortcut[];
}

// The action name behind every Ableton-shortcut remap (vs. smart actions like load_device).
export const SEND_KEYS_ACTION = "send_keys";

// What the edit modal operates on: either an existing binding (edit), or a not-yet-mapped
// catalog target picked from the unified list — a native Ableton shortcut (send_keys) or a
// smart action (load_device…). null = modal closed.
export type EditTarget =
  | { kind: "binding"; binding: Binding }
  | { kind: "ableton"; shortcut: AbletonShortcut }
  | { kind: "smart"; action: ActionDef }
  | null;

// /status: 3 states computed by the agent (Ableton absent / script inactive / ready).
export type AgentState = "no_ableton" | "script_inactive" | "ready";

export interface StatusResponse {
  state: AgentState;
  script_url?: string;
}
