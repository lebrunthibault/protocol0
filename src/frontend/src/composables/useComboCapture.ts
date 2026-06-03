// Capture de combo — LA source de vérité du raccourci enregistré.
//
// Porté depuis la page inline historique (_PAGE de shortcut_routes.py). On lit
// `event.code` (position physique de la touche) et PAS `event.key` (layout-dependent),
// pour produire EXACTEMENT la même chaîne canonique que le listener de l'agent (qui
// matche sur le `vk`, lui aussi positionnel). Parité garantie -> ce qu'on écrit est
// ce que l'agent déclenche.
//
// Ordre canonique : ctrl, alt, shift, win, puis la touche, minuscules, jointes par '+'.
// Namespace supporté : a-z, 0-9 (haut ET pavé numérique), f1-f12.
import { readonly, ref } from "vue";

const MOD_ORDER = ["ctrl", "alt", "shift", "win"] as const;

// e.code (position physique) -> touche canonique, ou null si non supportée.
export function keyName(code: string): string | null {
  let m: RegExpMatchArray | null;
  if ((m = code.match(/^Key([A-Z])$/))) return m[1].toLowerCase();
  if ((m = code.match(/^Digit([0-9])$/))) return m[1];
  if ((m = code.match(/^Numpad([0-9])$/))) return m[1];
  if ((m = code.match(/^F([0-9]{1,2})$/))) {
    const n = +m[1];
    if (n >= 1 && n <= 12) return "f" + n;
  }
  return null;
}

export function isModifier(code: string): boolean {
  return /^(Control|Alt|Shift|Meta|OS)/.test(code);
}

// Combo canonique depuis un KeyboardEvent, ou null si la touche n'est pas supportée.
export function buildCombo(e: KeyboardEvent): string | null {
  const mods: string[] = [];
  if (e.ctrlKey) mods.push("ctrl");
  if (e.altKey) mods.push("alt");
  if (e.shiftKey) mods.push("shift");
  if (e.metaKey) mods.push("win");
  const key = keyName(e.code);
  if (key === null) return null;
  const ordered = MOD_ORDER.filter((m) => mods.includes(m));
  return [...ordered, key].join("+");
}

export type CaptureStatus = "idle" | "recording" | "modifier" | "unsupported";

// Composable de capture attachable à un élément focusable. Pendant l'enregistrement,
// chaque keydown met à jour `combo` (la valeur enregistrée) et `status` (pour l'UI).
export function useComboCapture() {
  const combo = ref<string>("");
  const status = ref<CaptureStatus>("idle");

  function onKeydown(e: KeyboardEvent): void {
    e.preventDefault();
    e.stopPropagation();
    if (isModifier(e.code)) {
      status.value = "modifier"; // modificateur seul : on attend une vraie touche
      return;
    }
    const c = buildCombo(e);
    if (c === null) {
      status.value = "unsupported";
      return;
    }
    combo.value = c;
    status.value = "recording";
  }

  function start(): void {
    combo.value = "";
    status.value = "recording";
  }

  function clear(): void {
    combo.value = "";
    status.value = "idle";
  }

  return { combo: readonly(combo), status: readonly(status), onKeydown, start, clear };
}
