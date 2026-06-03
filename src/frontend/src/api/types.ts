// Contrat partagé avec l'agent (src/agent). Le schéma `shortcuts.json` est versionné
// (version 1) : un binding = { combo, action, params }. La combo est canonique
// (ctrl, alt, shift, win + touche, minuscules, jointes par '+') — identique à ce que
// le listener de l'agent matche.

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
  label: string;
  params: ActionParam[];
  path: string;
  method: string;
}

// /status : 3 états calculés par l'agent (Ableton absent / script inactif / prêt).
export type AgentState = "no_ableton" | "script_inactive" | "ready";

export interface StatusResponse {
  state: AgentState;
  script_url?: string;
}
