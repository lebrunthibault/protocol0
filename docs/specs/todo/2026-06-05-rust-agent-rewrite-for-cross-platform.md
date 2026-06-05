# Rust rewrite of the agent (ADR: cross-platform foundation)

Status: **investigation / architecture decision**, not yet scheduled. This spec records a
decision and the evidence behind it so the work can be picked up when the macOS port
becomes a committed goal. It does **not** call for a rewrite today.

## The decision in one line

Rewriting the **agent** in Rust (or Tauri) is justified **only as the enabler of a real
macOS port** — not for antivirus reasons, not for performance, not for "looking pro" on
Windows alone. When macOS ships, do it; until then, don't.

## What is and isn't on the table

The codebase has a hard architectural boundary:

```
[Keyboard] → protocol0-agent.exe (Python)        ← THIS is the rewrite candidate
                  │  HTTP localhost (runtime.json discovery)
                  ▼
        Ableton Live → Protocol_0 remote script (Python)   ← THIS stays Python forever
```

- The **remote script** (`src/remote-script/`, ~2000 LOC) runs **inside Ableton Live's embedded
  CPython**. It imports `Live` and `_Framework`, extends `ControlSurface`, and is
  instantiated by Live's bootstrap (`src/remote-script/protocol0/application/Protocol0.py`,
  `.../main.py::create_instance`). Ableton has standardized on Python control surfaces for
  15+ years; there is no non-Python control-surface API and no FFI bridge into Live's
  interpreter. **This is irreducibly Python and out of scope for any rewrite.**

- The **agent** (`src/agent/`, ~1500 LOC) is a standalone background process with **zero
  functional coupling to Ableton** — it talks to the script only over localhost HTTP. Its
  responsibilities: a global low-level keyboard hook (`WH_KEYBOARD_LL` via ctypes,
  `listener.py`), key injection (pynput, `key_emitter.py`), a `ThreadingHTTPServer` serving
  the Vue SPA + REST on `127.0.0.1:9010` (`web/server.py`), JSON config watching
  (`config.py`), a systray (`tray.py`, pystray), Ableton process/foreground detection
  (`process_check.py`, `foreground.py`), and a single-instance mutex
  (`single_instance.py`). **Every one of these has a mature cross-platform Rust equivalent.**

So the part that bothers us (a bundled-Python exe) is exactly the part that is portable.
The part that must stay Python is untouched by this question.

## Evidence gathered (OSS study, 2026-06-05)

Reference: **Espanso** (Rust text-expander, global keyboard hooks, systray, autostart,
Windows+macOS+Linux) — the closest comparable. Plus AutoHotkey, kanata/rdev, the Tauri
ecosystem, and Microsoft's own SmartScreen docs.

### 1. Antivirus / malware profile — Rust helps, but is NOT the fix

Three factors drive AV/SmartScreen flags. Rust improves only one of them:

| Factor | Impact | Does Rust help? |
| --- | --- | --- |
| Code signing + accrued reputation | **Decisive** for SmartScreen | No — language-independent |
| Keyboard-hook behaviour (`SetWindowsHookEx`/`WH_KEYBOARD_LL`) | High (heuristic/ML) | No — the API is what's flagged |
| PyInstaller shared bootloader signature | Medium | **Yes — this class disappears** |

- **Espanso, written in Rust with a keyboard hook, is still flagged**
  `Trojan:Win32/Bearfoos.A!ml`; the maintainer attributes it to *"Espanso's
  text-expansion functionality"* — the behaviour, not the language.
  ([espanso#2499](https://github.com/espanso/espanso/issues/2499))
- **AutoHotkey** (native C++) ships an official `.exe` flagged
  `Trojan:Script/Sabsik.FL.A!ml`. Same behavioural cause, no PyInstaller involved.
- **PyInstaller** maintainers acknowledge the shared-bootloader false-positive class and
  call themselves *"completely powerless"*
  ([pyinstaller#8164](https://github.com/pyinstaller/pyinstaller/issues/8164)). **This is
  the one vector a Rust rewrite genuinely removes.**
- Microsoft's
  [SmartScreen reputation doc](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/smartscreen-reputation):
  the only two signals are *signature* + *file-hash reputation*; an unsigned exe warns
  **regardless of language**, and **EV certs no longer bypass SmartScreen**.

**Conclusion:** switching to Rust while staying unsigned would likely cut the VirusTotal
hit count (shedding the PyInstaller class) but would **not** stop SmartScreen warnings or
the keyboard-hook heuristics. The real lever is **code signing** —
see `2026-06-02-installer-code-signing.md`. Do not rewrite in Rust *for AV reasons*.

### 2. "More pro / more reliable" — modest, mostly cosmetic

- One native binary, no bundled interpreter. Espanso v2.3.0 is **~6.5 MB** on Windows vs
  the current PyInstaller bundle (~70–100 MB, ships a full CPython 3.11). Instant start, no
  interpreter unpack.
- "Rust daemon" reads as more serious than "frozen Python exe" to devs/power users — real
  but qualitative. Perceived reliability comes mostly from signing + no AV warning (§1),
  not the language.

### 3. Robustness / performance — marginal for this workload

The agent is I/O-bound (waits on keystrokes, serves a few localhost requests). CPU is never
the bottleneck. Rust buys faster startup, lower memory, and static typing — but the agent
is small and stable. **Performance is not a real argument here.**

### 4. macOS port — the only strong argument, and it's nuanced

What Rust gives nearly for free, cross-platform and mature:

- **Systray**: `tray-icon` (Tauri team), Win+macOS. Caveat: macOS pins the tray to the main
  thread (`NSStatusItem` constraint, true in any language).
- **Local HTTP + embedded SPA**: `axum` + `rust-embed` — well-trodden; the Vue `dist/` can
  be baked into the binary.
- **File-watch / autostart / single-instance**: `notify`, `auto-launch` (Win+Mac),
  `single-instance` (the last is unmaintained since 2021 but trivially replaceable).

The hard part — **capturing AND suppressing a keystroke** — is *not* made easy by Rust:

- On macOS, Espanso captures with **passive `NSEvent` global monitors that cannot
  block/consume a key**. To consume a key (what `WH_KEYBOARD_LL` does on Windows) you need
  **`CGEventTapCreate`**. This matches our own constraint that a native, OS-level process is
  required (memory: keyboard-hook-must-be-native).
- Espanso's macOS backend is **Objective-C++ (`.mm`) wrapped via FFI**, not pure Rust
  (~13 KB of native detect+inject glue, plus Cocoa for the tray). The Rust `rdev` crate's
  `grab`/suppress is feature-gated `unstable` and under-documented on Windows. **Per-OS
  native glue is unavoidable in any language.**
- **macOS permissions**: Accessibility + Input Monitoring are mandatory, prompt repeatedly,
  and re-prompt whenever the signing cert changes (espanso#2562, #2031, #2402). Rust solves
  none of this.
- **Notarization**: ~$99/yr Apple Developer + non-trivial CI. Espanso shipped **unsigned for
  ~3 years** before tackling it.

**The real point:** the hard parts of the Mac port — the `CGEventTap` backend, the macOS
permission UX, notarization — are **identical in Python and Rust**. What Rust changes is
that **everything else (HTTP, systray, config, autostart, single-instance) becomes
cross-platform for almost nothing**, whereas Python's macOS packaging story (PyInstaller on
mac + notarizing a Python bundle) is even more painful than Windows. That asymmetry — not
performance or AV — is the case for Rust.

## Tauri v2 as the likely concrete path

Because a Vue SPA already exists, **Tauri v2** subsumes most of the scaffolding as
first-party features: built-in tray, official autostart / single-instance / updater
plugins, and **first-class macOS `.app` bundling + code signing + notarization**. The
existing localhost REST API can either be kept as an embedded `axum` server (if other local
tools must reach it) or collapsed into Tauri `invoke` commands. Cost: it ships a WebView we
may not strictly need. For a UI-bearing daemon targeting Win+macOS, Tauri is likely the
*less* sharp-edged path than hand-assembling crates. **To be evaluated at pickup time**
against a plain `axum` + `tray-icon` + native-hook-glue assembly.

## Scope (if/when picked up)

Prerequisite: macOS support is a committed, scheduled goal. Do **not** start otherwise.

1. **Decide shell**: Tauri v2 vs hand-rolled (`axum` + `tray-icon` + `notify` +
   `auto-launch`). Lean Tauri given the existing Vue SPA and the macOS signing/notarization
   help it provides.
2. **Port the portable 80%**: HTTP server + embedded SPA, JSON config + watch, systray,
   process/foreground detection, single-instance, autostart, `runtime.json` discovery of
   the script URL. Keep the HTTP contract with the remote script **byte-for-byte unchanged**
   (the script stays Python and must not notice the swap).
3. **Write the native hook glue per OS**: Windows `WH_KEYBOARD_LL` + `SendInput`; macOS
   `CGEventTap` (capture *and* suppress) + `CGEventPost` injection. This is the irreducible
   native work; budget real per-OS testing for suppression fidelity.
4. **macOS permissions + packaging**: Accessibility + Input Monitoring prompts and guidance;
   `.app` bundle; Developer ID signing + notarization (Apple Developer Program). Coordinate
   the signing identity with `2026-06-02-installer-code-signing.md` so reputation compounds.
5. **Keep the remote script untouched.** Verify the new agent against the existing
   `/openapi.json` + `/api/action/*` contract.

## Out of scope

- **Rewriting the remote script** — impossible (runs inside Ableton's CPython).
- **A Rust rewrite for AV or performance reasons on Windows alone** — the evidence does not
  support it; sign the existing exe instead (`2026-06-02-installer-code-signing.md`).
- **Linux** — not a target.

## Relationship to other specs

- `2026-06-02-installer-code-signing.md` — the *actual* fix for the AV/SmartScreen friction,
  and a hard prerequisite for the macOS port (notarization). This is higher priority than
  the rewrite.
- `2026-06-05-systray-and-startup-folder-autostart.md` — the current Windows systray +
  Startup-folder autostart model that a Rust/Tauri agent would have to reproduce
  cross-platform.

## Priority

Low / deferred. Gated entirely on macOS becoming a committed goal. Until then this is a
recorded decision, not queued work. When macOS is greenlit, this becomes the foundation
spec for that effort, and code signing (Windows Authenticode + macOS notarization) lands
first.
