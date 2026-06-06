# Installer code signing (Authenticode)

## Problem

`Protocol0-Setup-<version>.exe` (and the `protocol0-agent.exe` it carries) is signed by no
Authenticode certificate. At runtime the UAC box shows
**"Publisher: Unknown"** in yellow, and Windows SmartScreen warns on first launch
("Windows protected your PC"). Combined with the fact that the agent is a global
**keyboard hook** built with **PyInstaller** — the textbook keylogger/dropper profile —
this reads as untrustworthy, especially when distributed beyond the personal circle.

Note: the `.iss` field `MyAppPublisher "Thibault Lebrun"` has **no** effect on the UAC
box (which reads only the cryptographic signature); it only shows up in "Programs and
Features" after install. The installer is admin-required anyway (it writes to Program
Files + `C:\ProgramData\Ableton`), so the UAC prompt always appears — signing only
changes its colour/text.

## What changed since the first draft (correction)

The original version of this backlog claimed an **EV certificate removes the SmartScreen
warning on the first signature**. **This is no longer true** (verified against current
Microsoft docs, 2026-05). Microsoft, *"SmartScreen reputation for Windows app developers"*:

> "EV certificates no longer bypass SmartScreen. Years ago, signing files with an
> Extended Validation (EV) code signing certificate would result in positive SmartScreen
> reputation by default, but this behavior no longer exists. … Paying a premium for EV
> solely to avoid SmartScreen warnings is no longer justified."

**No certificate, at any price, clears SmartScreen instantly** for non-Store
distribution. SmartScreen is purely reputation-based — keyed on **file hash** and
**publisher certificate** — and accrues over weeks of clean downloads. Only the
Microsoft Store (which re-signs apps) is never subject to SmartScreen.

Consequences for our choice:
- **Do not buy an EV cert with a hardware dongle.** It no longer buys the one thing it
  used to (instant SmartScreen pass) and is the most expensive/awkward option.
- Signing still matters — but for a **different** reason than this backlog first stated.

## What signing actually buys us

- Removes the **"Unknown Publisher"** UAC warning and displays the verified publisher
  name (this is immediate).
- Builds **reputation against a stable signing identity**: SmartScreen reputation cannot
  transfer between releases *unless they share the same publisher identity*. So a stable
  cert lets each new release inherit the publisher's accumulated reputation — the warning
  fades organically over weeks. **Never rotate the cert.**

It does **not** make SmartScreen disappear on day one. That only comes with time (or the
Store).

## Recommended path: SignPath Foundation (free, for OSS)

[SignPath Foundation](https://signpath.org/) gives **free OV-level Authenticode signing**
to open-source projects (OSI license, no proprietary components, actively maintained,
every release manually approved). It is the right fit for Protocol0 as an OSS project,
and it is proven by directly comparable repos:

- **OptiKey** (on-screen keyboard / accessibility, i.e. keyboard-adjacent) —
  `.github/workflows/release_all.yml` uses `signpath/github-action-submit-signing-request`.
- **novelWriter** (solo-dev PyInstaller desktop app) — same action.
- **sabnzbd** (desktop daemon) — same action.

Pattern: CI builds → `actions/upload-artifact` → `signpath/github-action-submit-signing-request`
submits the artifact and downloads the signed binary back. Sign **both** exes (agent +
launcher) and the Setup. Timestamping (`/tr <rfc3161>` `/td SHA256`) is handled by the
signing toolchain and is essential so binaries stay valid after the cert expires.

## Fallback: Azure Trusted Signing (~$10/mo) — with an eligibility gotcha

Azure "Trusted Signing" (now "Artifact Signing") is the modern cheap alternative (no
hardware token, CI-friendly, defaults its timestamp to `http://timestamp.acs.microsoft.com`).
**But the individual-developer validation path is USA/Canada only.** Per Microsoft's
Artifact Signing FAQ, the individual path is available only to developers in the USA and
Canada; the EU/UK are covered only for **organizations**. As an individual EU/UK developer,
the publisher (Thibault Lebrun) is **not eligible** for the individual path — this rules
Trusted Signing out unless a qualifying organization is set up. **→ SignPath is therefore
the clear choice here.** It also does not issue EV (by design), consistent with the
correction above.

## Scope (if/when this is picked up)

- **Apply to SignPath Foundation** as an OSS project (one-time; manual per-release
  approval thereafter). No purchase.
- **Wire signing into `release.yml`**: add the SignPath submit-signing-request step after
  the build, signing `protocol0-agent.exe` and
  `Protocol0-Setup-<version>.exe`. Inno Setup also supports a `SignTool` directive in
  `installer/protocol0.iss` if signing the Setup at compile time is preferred.
- **Keep the signing identity stable across releases** (so publisher reputation
  compounds). Document this constraint.
- **Document** the procedure (where the SignPath project lives, that nothing secret is
  committed — SignPath holds the key, CI only holds an API token in a repo secret).

## Out of scope

- **EV certificate / hardware dongle** — no longer justified (see correction above).
- **Self-signed certificate** — only removes the warning on machines where the cert is
  imported into the trust store; useless for distribution.
- **Making the installer non-admin** — impossible while the remote script lives under
  `C:\ProgramData\Ableton` (imposed by Ableton). Unrelated to signing.

## Relationship to install-trust

The cheap, no-cert trust/AV moves (README "is this a keylogger?" section, SHA256SUMS,
build-provenance attestations, VirusTotal links, PE version metadata) are split into a
separate, higher-priority spec — see `2026-06-04-install-trust-and-av.md`. Those land
first and carry most of the friction reduction at near-zero cost. Code signing is the
durable structural fix layered on top, once the per-release VirusTotal/WDSI submission
tax becomes painful.

## Priority

Low while usage stays personal / small-circle — the yellow UAC warning is tolerable.
The install-trust spec is the higher-leverage, do-first work.
