# Installer code signing (Authenticode)

> **Status: in-progress.** Pipeline wired for **SignPath Foundation** (two-stage signing —
> `Protocol0.exe` then the installer) in `.github/workflows/release.yml`, gated on the
> `SIGNPATH_API_TOKEN` secret so the release still builds **unsigned** until the SignPath project
> is provisioned. Remaining (out-of-repo): apply to SignPath Foundation, set the `SIGNPATH_API_TOKEN`
> secret + `SIGNPATH_ORGANIZATION_ID` repo variable, configure the two artifact configurations
> (`agent-exe`, `installer`) + the `release-signing` policy, then validate with a test-tag release.

## Problem

`Protocol0-Setup-<version>.exe` (and the resident `Protocol0.exe` agent it carries) is signed by
no Authenticode certificate. At runtime the UAC box shows **"Publisher: Unknown"** in yellow, and
Windows SmartScreen / Defender warn on a fresh download. The agent is a global **keyboard hook** —
the textbook keylogger profile — so an unsigned binary reads as untrustworthy when distributed
beyond the personal circle.

Concretely observed (0.18.2): Chrome blocked the download as "Virus detected". This was **Defender
local** (`Trojan:Win32/Wacatac.H!ml`, a `!ml` ML-cloud verdict on a new/rare/unsigned binary,
surfaced via *block at first sight*), **not** Google Safe Browsing. It is non-deterministic per
hash — v0.1.1 passed, 0.18.2 didn't — so a stable signing identity is the durable fix: it stops
Defender treating every release as "never seen", letting reputation accrue instead of resetting
each hash. (The immediate per-hash mitigation is a WDSI false-positive submission — see the
`/release` skill, step 7.)

> **Correction — the agent is no longer PyInstaller.** It is now a **native Rust binary**
> (`src/agent`, ~3 MB, Vue SPA embedded via rust-embed), so the "shared PyInstaller bootloader"
> false-positive class is gone, and there is **only one exe** (`Protocol0.exe`; the separate
> launcher was dropped, commit `a357bdf1`). Any earlier mention of `protocol0-agent.exe` /
> `protocol0-launcher.exe` / PyInstaller in this spec is obsolete.

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

Pattern (implemented): CI builds the agent exe → `actions/upload-artifact` →
`signpath/github-action-submit-signing-request` signs it and downloads the signed binary back →
ISCC packages the **signed** exe → the installer is uploaded, signed, and restored the same way.
SignPath signs only via a **GitHub artifact id** (not a disk path), hence the upload/sign/restore
round-trip per stage. We sign **both** the agent exe and the installer — the resident agent runs a
keyboard hook and is re-scanned by Defender on **every launch**, so it needs its own signature,
not just the installer's (best practice, mirrors OptiKey's two-stage `release_all.yml`).
Timestamping (RFC3161) is handled by the signing toolchain and is essential so binaries stay valid
after the cert expires.

## Alternative: Azure Trusted Signing (~$10/mo) — now EU-eligible (plan B)

Azure "Trusted Signing" (now "Artifact Signing") is the cheap modern option (no hardware token,
CI-friendly, default timestamp `http://timestamp.acs.microsoft.com`).

> **Correction (2026-06).** Earlier drafts ruled Azure out for EU developers. **No longer true.**
> The Azure portal now states Artifact Signing is *"available to organizations in the USA, Canada,
> **European Union & United Kingdom**"*, and the publisher's French micro-entreprise (7 yrs,
> qualifies the ≥3-yr org rule) is mid identity-validation. Azure is therefore **eligible** via the
> **organization** path.

It remains positioned as **plan B, mutually exclusive with SignPath** — not a co-signer. Decision:
ship SignPath first (free, OSS-native, already wired). If Defender/SmartScreen keep flagging after
1–2 signed releases despite a stable identity, switch to Azure and **remove** SignPath (never run
two signing identities in parallel — reputation must compound on one). The `release.yml` signing
steps are isolated and marked (`# === SIGNING (provider: SignPath) — swap here for Azure ===`) so
the swap edits only those two `uses:` blocks (→ `azure/trusted-signing-action` + `azure/login`).
Neither path issues EV (consistent with the correction above).

## Scope

**Done in-repo (this change):**
- `release.yml` wired for two-stage SignPath signing (`Protocol0.exe` then the installer), placed
  **before** `Generate SHA256SUMS` + `Attest build provenance` so the published hash and the
  Sigstore attestation cover the **signed** binary. Steps are gated on `SIGNING_ENABLED`
  (derived from the `SIGNPATH_API_TOKEN` secret) — the release still builds unsigned without it.
- `installer/windows/build_installer.ps1` gained a `-Stage agent|installer|all` parameter so CI can
  sign the exe **between** building it and ISCC embedding it. Local build (`-Stage all`, the
  default) is unchanged and unsigned.
- We sign **post-compile via the action**, so **no** `SignTool=` directive is added to
  `installer/windows/protocol0.iss` (the local build stays cert-free and functional).

**Remaining (out-of-repo, one-time, by maintainer):**
- **Apply to SignPath Foundation** as an OSS project (manual per-release approval thereafter; no
  purchase).
- In SignPath: create project `protocol0`, signing policy `release-signing`, and two artifact
  configurations — `agent-exe` and `installer` (the slugs referenced by the workflow).
- Set repo **secret** `SIGNPATH_API_TOKEN` and repo **variable** `SIGNPATH_ORGANIZATION_ID`.
  Nothing secret is committed — SignPath holds the key; CI holds only the API token.
- **Keep the signing identity stable across releases** so publisher reputation compounds. Never
  rotate the cert; never run SignPath and Azure in parallel.

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

Picked up now: the install-trust spec (the cheap no-cert moves) has shipped, and a concrete
Defender download-block on 0.18.2 made the per-hash WDSI tax real. Code signing is the durable
structural fix on top — in-repo wiring is done; only the out-of-repo SignPath provisioning remains.
