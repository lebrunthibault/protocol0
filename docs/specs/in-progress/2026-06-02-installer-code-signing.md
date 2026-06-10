# Installer code signing (Authenticode)

> **Status: in-progress.** Pipeline wired for **Azure Trusted / Artifact Signing** (two-stage:
> `Protocol0.exe` then the installer) in `.github/workflows/release.yml`, gated on
> `AZURE_CLIENT_SECRET` so the release still builds **unsigned** in forks without the secrets.
> The maintainer's Azure organization identity validation **succeeded** and the three `AZURE_*`
> secrets (service principal) are set on the repo. Remaining: validate with a test-tag release
> (signature chain + "Publisher: Thibault Lebrun" on the UAC box).
>
> **Provider history:** SignPath Foundation was the original plan (free, OSS) and is fully
> documented below as the **backlog alternative** — kept because it's a clean fallback if the
> Azure subscription ever lapses. Azure won because the EU-organization path reopened and the
> maintainer's validation went through; running **one** signing identity (not both) is required so
> reputation compounds.

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

## Chosen path: Azure Trusted / Artifact Signing (~$10/mo, organization identity)

Azure "Trusted Signing" (now "Artifact Signing") is a CI-friendly cloud signing service: no
hardware token, certs managed by Azure, default timestamp `http://timestamp.acs.microsoft.com`.

> **Eligibility (2026-06).** Earlier drafts ruled Azure out for EU developers. **No longer true.**
> The Azure portal now states Artifact Signing is *"available to organizations in the USA, Canada,
> **European Union & United Kingdom**"*. The publisher's French micro-entreprise (7 yrs, qualifies
> the ≥3-yr org rule) completed **organization identity validation** → eligible via the org path.

**Implemented** in `release.yml` via `azure/trusted-signing-action@v0.5.0`. Azure signs files
**in place on the runner disk** (no artifact upload/download round-trip — simpler than SignPath):

- **Stage 1** signs `src/agent/target/release/Protocol0.exe` (explicit `files:` path) right after
  the agent is built, **before** ISCC embeds it.
- **Stage 2** signs the installer (`files-folder: dist-installer`, `files-folder-filter: exe`,
  because the filename carries the version) after ISCC, **before** SHA256SUMS + attestation.

We sign **both** the agent exe and the installer — the resident agent runs a keyboard hook and is
re-scanned by Defender on **every launch**, so it needs its own signature, not just the installer's
(best practice, mirrors OptiKey's two-stage signing). RFC3161 timestamping is set explicitly so
binaries stay valid after the cert rotates.

Config (non-secret) lives in the job `env`: `SIGNING_ENDPOINT`
(`https://eus.codesigning.azure.net/`), `SIGNING_ACCOUNT_NAME` (`protocol0signing`),
`SIGNING_CERT_PROFILE` (`protocol0profile`). Secrets: `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`,
`AZURE_CLIENT_SECRET` (an App Registration service principal). `SIGNING_ENABLED` derives from
`AZURE_CLIENT_SECRET` so forks without the secret still build (unsigned).

## Backlog alternative: SignPath Foundation (free, for OSS)

Kept as the documented fallback if the Azure subscription ever lapses — **do not run both**
(reputation must compound on a single identity). [SignPath Foundation](https://signpath.org/) gives
**free OV-level Authenticode signing** to OSS projects (OSI license, no proprietary components,
per-release manual approval), proven by directly comparable repos:

- **OptiKey** (on-screen keyboard / accessibility, keyboard-adjacent) — uses
  `signpath/github-action-submit-signing-request`.
- **novelWriter** (solo-dev desktop app) — same action.
- **sabnzbd** (desktop daemon) — same action.

SignPath signs only via a **GitHub artifact id** (not a disk path), so its pattern is
upload-artifact → sign → download-signed-back per stage (heavier than Azure's in-place signing).
To switch back, replace the two `# === SIGNING (provider: Azure) ===` steps in `release.yml` with
the SignPath action, add a project (`protocol0`), policy (`release-signing`) and two artifact
configurations (`agent-exe`, `installer`), and set `SIGNPATH_API_TOKEN` + `SIGNPATH_ORGANIZATION_ID`.
Neither provider issues EV (consistent with the correction above).

## Scope

**Done in-repo (this change):**
- `release.yml` wired for two-stage **Azure** signing (`Protocol0.exe` then the installer) via
  `azure/trusted-signing-action@v0.5.0`, placed **before** `Generate SHA256SUMS` +
  `Attest build provenance` so the published hash and the Sigstore attestation cover the **signed**
  binary. Steps are gated on `SIGNING_ENABLED` (derived from `AZURE_CLIENT_SECRET`) — forks without
  the secret still build unsigned.
- `installer/windows/build_installer.ps1` gained a `-Stage agent|installer|all` parameter so CI can
  sign the exe **between** building it and ISCC embedding it. Local build (`-Stage all`, the
  default) is unchanged and unsigned.
- We sign **post-compile via the action**, so **no** `SignTool=` directive is added to
  `installer/windows/protocol0.iss` (the local build stays cert-free and functional).

**Done out-of-repo (by maintainer):**
- Azure organization identity validation **passed**; signing account `protocol0signing` + cert
  profile `protocol0profile` created (endpoint `https://eus.codesigning.azure.net/`).
- Repo secrets `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET` (App Registration
  service principal with the *Trusted Signing Certificate Profile Signer* role) set.

**Remaining:**
- Validate end-to-end on a **test-tag release**: `signtool verify /pa` on both binaries, and the
  UAC box showing **"Publisher: Thibault Lebrun"**.
- **Keep one stable signing identity** so publisher reputation compounds — never rotate; never run
  Azure and SignPath in parallel.

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
