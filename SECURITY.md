# Security

## Is this a keylogger? Why does my antivirus flag it?

**Short answer: no, it isn't — and yes, your antivirus may flag it anyway. Here's
exactly why, and how to verify the download yourself.**

Protocol 0 needs a **global keyboard hook** to do its one job: catch a shortcut
(say `Ctrl+Alt+L`) no matter which window has focus, and run the action you mapped
to it. Watching keys globally is, mechanically, the same thing a keylogger does —
so antivirus heuristics and Windows SmartScreen treat any unsigned tool that does
it with suspicion. That suspicion is about the *shape* of the program, not evidence
of anything malicious.

What the agent actually does with your keystrokes:

- It installs a low-level Windows keyboard hook (`SetWindowsHookExW` /
  `WH_KEYBOARD_LL` — see [`src/agent/agent/listener.py`](src/agent/agent/listener.py)).
- For every key, it checks **only** whether the current combination matches one of
  *your* configured shortcuts, **and** whether Ableton is the focused window. If
  not, the key is passed straight through, untouched.
- It **logs nothing, buffers no text, and types nothing into a file**. The only
  state it keeps is which modifier/keys are physically held right now (so it can
  recognise a combo and not double-fire) — in memory, discarded as you release the
  keys. There is no keystroke history anywhere.
- The **only** file it persists is your shortcut mapping,
  `%APPDATA%\Protocol0\shortcuts.json`, written from the web UI — never from the
  keyboard listener.
- It makes **no outbound network calls**. Everything is local: the agent talks only
  to `127.0.0.1` (its own web UI on `:9010`, and the remote script inside Ableton).
  It never phones home, downloads, or launches anything.

Why your antivirus may still warn:

- The agent is built with **PyInstaller**, whose bootloader is byte-identical across
  every tool built with it — so it shares a hash that some antivirus ML models have
  learned to distrust. Combined with the keyboard hook, an **unsigned** PyInstaller
  exe is a textbook false-positive trigger. This is heuristics, not detection.
- The installer is **not yet code-signed** (signing is on the roadmap — see
  [`docs/specs/backlog/2026-06-02-installer-code-signing.md`](docs/specs/backlog/2026-06-02-installer-code-signing.md)),
  so SmartScreen shows "unknown publisher" until reputation builds up.

How to verify the download yourself, without trusting us:

- **Read the source.** It's all here. The entire keyboard path is one small file:
  [`listener.py`](src/agent/agent/listener.py).
- **Check the hash.** Every release ships a `SHA256SUMS` asset; compare it against
  the `.exe` you downloaded (`Get-FileHash Protocol0-Setup-<version>.exe`).
- **Verify the build provenance.** Every release binary carries a signed
  [provenance attestation](https://docs.github.com/en/actions/security-for-github-actions/using-artifact-attestations/verifying-attestations-offline)
  proving it was built by this repo's public CI from a tagged commit:
  ```
  gh attestation verify Protocol0-Setup-<version>.exe -R lebrunthibault/protocol0
  ```
- **Upload it to [VirusTotal](https://www.virustotal.com/)** and see for yourself —
  a handful of heuristic flags amid dozens of clean verdicts is the signature of a
  false positive, not malware. (Release notes also link a VirusTotal scan.)

## Reporting a vulnerability

Found a genuine security issue? Please report it privately by email to
**thibaultlebrun@live.fr** rather than opening a public issue.
