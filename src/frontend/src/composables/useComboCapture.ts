// Combo capture — THE source of truth for the recorded shortcut.
//
// LETTERS: layout-aware via `event.key` (the keycap character: Q -> "q" on AZERTY),
// to match what the user reads on their key. On the agent side, the listener resolves
// letters the same way (pynput `canonical`, independent of modifiers).
// EVERYTHING ELSE (digits, numpad, f1-f12, named keys): positional via
// `event.code`, in sync with the agent's `vk`. (On AZERTY the digit row
// requires Shift, so a layout-aware lookup would yield punctuation — hence the
// hybrid choice: letters by layout, digits by position.) Capture/agent parity guaranteed.
//
// Canonical order: ctrl, alt, shift, win, then the key, lowercase, joined by '+'.
import { readonly, ref } from "vue";

const MOD_ORDER = ["ctrl", "alt", "shift", "win"] as const;

// e.code (physical position) of named keys -> canonical token.
// Includes the numpad variants (NumpadEnter) that share the same token.
const NAMED_CODES: Record<string, string> = {
  Space: "space",
  Tab: "tab",
  Enter: "enter",
  NumpadEnter: "enter",
  Escape: "esc",
  Backspace: "backspace",
  Delete: "delete",
  ArrowUp: "up",
  ArrowDown: "down",
  ArrowLeft: "left",
  ArrowRight: "right",
  Home: "home",
  End: "end",
  PageUp: "pageup",
  PageDown: "pagedown",
};

// e.code (physical position) -> canonical POSITIONAL key, or null if unsupported.
// Used for digits / numpad / f-keys / named keys (not letters).
export function keyName(code: string): string | null {
  let m: RegExpMatchArray | null;
  if ((m = code.match(/^Digit([0-9])$/))) return m[1];
  if ((m = code.match(/^Numpad([0-9])$/))) return m[1];
  if ((m = code.match(/^F([0-9]{1,2})$/))) {
    const n = +m[1];
    if (n >= 1 && n <= 12) return "f" + n;
  }
  return NAMED_CODES[code] ?? null;
}

export function isModifier(code: string): boolean {
  return /^(Control|Alt|Shift|Meta|OS)/.test(code);
}

// Canonical name of a key from the event: layout-aware letter (e.key) otherwise
// positional fallback (e.code). null if out of namespace.
export function keyFromEvent(e: KeyboardEvent): string | null {
  // e.key is the character of the current layout (AZERTY: the Q key returns "q"), and
  // browsers provide it even under Ctrl/Alt for letters.
  if (e.key && e.key.length === 1 && /[a-zA-Z]/.test(e.key)) {
    return e.key.toLowerCase();
  }
  // AltGr (= Ctrl+Alt) on AZERTY turns e.key into a glyph (key E -> "€"), which
  // falls outside the a-z test above. We then fall back to the physical code KeyX, in sync
  // with the agent's `vk` resolution (keymap.py), so that ctrl+alt+e works.
  const m = e.code.match(/^Key([A-Z])$/);
  if (m) return m[1].toLowerCase();
  return keyName(e.code);
}

// Canonical combo from a KeyboardEvent, or null if the key is not supported.
export function buildCombo(e: KeyboardEvent): string | null {
  const mods: string[] = [];
  if (e.ctrlKey) mods.push("ctrl");
  if (e.altKey) mods.push("alt");
  if (e.shiftKey) mods.push("shift");
  if (e.metaKey) mods.push("win");
  const key = keyFromEvent(e);
  if (key === null) return null;
  const ordered = MOD_ORDER.filter((m) => mods.includes(m));
  return [...ordered, key].join("+");
}

export type CaptureStatus = "idle" | "recording" | "modifier" | "unsupported";

// Capture composable attachable to a focusable element. During recording,
// each keydown updates `combo` (the recorded value) and `status` (for the UI).
export function useComboCapture() {
  const combo = ref<string>("");
  const status = ref<CaptureStatus>("idle");

  function onKeydown(e: KeyboardEvent): void {
    e.preventDefault();
    e.stopPropagation();
    if (isModifier(e.code)) {
      status.value = "modifier"; // modifier alone: we wait for a real key
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

  // Force a combo (e.g. chosen from the menu of reserved shortcuts the browser
  // won't let us capture: Ctrl+N/T/W). The combo is assumed already canonical.
  function set(value: string): void {
    combo.value = value;
    status.value = "recording";
  }

  return { combo: readonly(combo), status: readonly(status), onKeydown, start, clear, set };
}
