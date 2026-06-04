# Install trust & AV friction (no-cert, do-first)

> **Shipped (conforme).** Tous les items livrés : (1) `SECURITY.md` + lien README,
> (2) `SHA256SUMS` en CI, (3) `attest-build-provenance`, (4) métadonnées PE sur les
> deux exes (`version_info.py`), (5) scan VirusTotal, (6) note de soumission
> faux-positif WDSI dans la skill `/release` (Étape 7). Tout sauf 1–5 a été fait
> dans le commit `1beeb174` ; item 6 + bump `attest-build-provenance@v2→@v4`
> ajoutés ensuite.

Lower the friction and distrust at install time **without buying a certificate**. The
agent is a global keyboard hook built with PyInstaller — the textbook
keylogger/dropper profile — so an unsigned `.exe` draws AV false positives and
"is this malware?" hesitation. These moves are cheap (mostly free, mostly one-time),
attack the **trust friction** directly, and land before the code-signing work
(`docs/specs/backlog/2026-06-02-installer-code-signing.md`), which is the durable but
costlier structural fix on top.

This is **Windows-only** like the rest of the packaging tooling.

## Why this first (and why not just sign)

Verified against current Microsoft docs (2026-05): **no certificate at any price clears
SmartScreen instantly** for non-Store distribution — SmartScreen is reputation-based
(file hash + publisher identity), accruing over weeks. EV no longer bypasses it. So
signing is necessary-but-not-sufficient and is deferred. The highest impact-per-effort
right now is **transparency + release hygiene**, proven by comparable suspicious-by-design
OSS tools (espanso, AutoHotkey, kanata, Syncthing).

This is the concrete form of the project's standing intent to attack the *trust* friction
of a keyboard hook, not the technique.

## Scope

### 1. "Is this a keylogger? Why does my AV flag it?" — in SECURITY.md (highest impact)

A dedicated `SECURITY.md` (so GitHub surfaces a "Security policy" tab, and the README stays
clean and non-scary for users with no problem), linked from the README's SmartScreen install
bullet ("Worried about security, or did your antivirus flag it? See SECURITY.md"). Modelled on
[espanso's SECURITY.md](https://github.com/espanso/espanso/blob/master/SECURITY.md) and
[AutoHotkey's FAQ #Virus](https://www.autohotkey.com/docs/v2/FAQ.htm#Virus). It must:

- Name the suspicion plainly and refute it: the agent detects key presses **as a
  keylogger would**, but **logs nothing** and **sends nothing off the machine** (the
  agent's own spec comments already note "no outbound network call, no download/launch of
  an exe" — surface that to users).
- State exactly what is and isn't stored: bindings live in
  `%APPDATA%\Protocol0\shortcuts.json`; key events are matched against bindings, not
  persisted or transmitted.
- Name the OS mechanism (the Windows keyboard hook via `pynput`) and **why** the hook
  can't live inside Ableton's embedded Python (already explained in the README
  architecture section — cross-reference it).
- Explain **why AV flags it**: unsigned PyInstaller exe + keyboard hook = heuristic match,
  not infection. Tell users they can upload to VirusTotal and audit the source.
- End with "the binary you download is built in public CI from a tagged commit — verify
  it" (ties into items 2–3).

Acceptance: a worried user has one URL that answers "is this safe?" end to end.

### 2. SHA256SUMS on every release

Emit a `SHA256SUMS` file as a release asset in `release.yml` (kanata does exactly this).
One CI step computing the hash of `Protocol0-Setup-<version>.exe`. Document the one-line
verification in the README.

### 3. Build-provenance attestation (free substitute for signing)

Add `actions/attest-build-provenance@v4` to `release.yml` with the installer as
`subject-path`. This is a free, Sigstore-backed "this binary was built by this workflow,
from this commit" proof — the closest no-cert analogue to code signing. Document the
consumer command in the README:

```
gh attestation verify Protocol0-Setup-<version>.exe -R lebrunthibault/protocol0
```

Requires `attestations: write` (and `id-token: write`) in the workflow `permissions`.

### 4. PE version metadata on both exes

Both `protocol0-agent.spec` and `protocol0-launcher.spec` currently pass **no**
`version=` to `EXE()`. Add a PyInstaller version-info resource (CompanyName, ProductName,
FileDescription, version pulled from the root `VERSION`, copyright). Populated PE metadata
is a positive trust signal for AV ML models and makes the binary look like "a real app".
One-time; regenerate the version block from `VERSION` at build time so it doesn't drift
(mirror how the `.iss` reads `VERSION`).

### 5. VirusTotal scan link per release

Add `cssnr/virustotal-action` (or `crazy-max/ghaction-virustotal`) to `release.yml` to
scan the installer and append the VT result link to the release notes. Free; one-time CI
setup, runs per release. Requires a free VirusTotal API key in a repo secret.

### 6. (Optional, low cost) Microsoft WDSI false-positive submission note

Document in the release skill / runbook that if a release is flagged, submit the hash to
<https://www.microsoft.com/wdsi/filesubmission> (and other vendors). This is per-hash, so
it recurs per release until signing builds certificate reputation — hence a manual runbook
note, not automation.

## Already in place (do not redo)

- `upx=False` in both `.spec` files — correct; UPX compression is a known AV trigger.
- `console=False` — no console flash.
- The agent makes **no outbound network calls** — a real trust asset; just surface it to
  users (item 1).

## Explicitly NOT in this spec

- **`--onefile` → `--onedir`.** Tempting (onefile unpacks to temp at runtime, a
  dropper-like heuristic), but **not free here**: the agent embeds the Vue SPA and
  `VERSION` via `datas` and reads them through `sys._MEIPASS`
  (`agent/web/static_files.py`, `agent/version.py`), a mechanism that depends on onefile
  extraction. Switching to onedir means reworking that path resolution and the `.iss`
  `[Files]` layout. Real trade-off, separate spec if pursued.
- **Code signing** — see `2026-06-02-installer-code-signing.md` (SignPath, deferred).
- **winget / Scoop listing** — discoverability + a trust signal, but **orthogonal to
  SmartScreen/AV** (Microsoft confirms reputation is hash+cert only, never the package
  manager). Worth doing, tracked separately so it doesn't dilute this AV-focused spec.
- **Rebuilding the PyInstaller bootloader** to change its shared hash — possible but
  fiddly and low-yield next to signing; skip unless a specific bootloader-hash flag
  appears.

## Verification

- A single README URL answers "is this a keylogger / why does AV flag it / how do I
  verify the download".
- A release carries: the installer, a `SHA256SUMS` asset, a provenance attestation
  (`gh attestation verify` passes), a VT scan link in the notes.
- Both exes show populated File Properties → Details (product name, version, description)
  in Windows Explorer.

## Depends on

- Jalon 1/2 installer + `release.yml` merged (the workflow these steps hook into).
