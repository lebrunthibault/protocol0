# Protocol 0 — website

The marketing landing page and documentation for [Protocol 0](https://github.com/lebrunthibault/protocol0).

Static site, zero build step. Plain HTML + CSS + a little vanilla JS. The visual
language follows the design handoff (dark, Mirai-inspired): `Schibsted Grotesk`
for text, `JetBrains Mono` for keycaps/code, the `#4d9fff` blue accent.

## Structure

```
src/website/
├── index.html          Landing page
├── design-system.css   Design tokens + all shared components (source of truth)
├── DESIGN.md           How to reuse the design system in another surface
├── vercel.json         Deployment config (headers, URL handling)
├── api/
│   └── subscribe.js     Newsletter signup — Vercel serverless function → Resend
├── docs/
│   ├── docs.css         Docs layout (sidebar + prose)
│   ├── index.html       Docs overview
│   ├── installation.html
│   ├── architecture.html
│   ├── extending.html
│   └── faq.html
└── README.md           (this file)
```

All internal links are root-absolute (`/`, `/docs/…`, `/design-system.css`), so the site
must be served from the **root of the deployment** — which is exactly what
pointing Vercel at this folder does.

## Local preview

No build needed. Serve the folder with any static server, e.g.:

```sh
# Python
python -m http.server 3000        # then open http://localhost:3000

# Node
npx serve .
```

Opening `index.html` directly via `file://` mostly works, but the root-absolute
links (`/docs/`, `/design-system.css`) resolve against the filesystem root, so use a
local server for an accurate preview.

Static servers do **not** run the serverless function — `/api/subscribe` will 404
and the newsletter form will show its error state. To exercise the form locally,
use `vercel dev` (see Newsletter below).

## Deploy on Vercel

This folder is self-contained and deploys as a static site with **no build
command**.

1. Import the `protocol0` repo into Vercel (New Project → Import Git Repository).
2. Set **Root Directory** to `src/website`.
3. Framework Preset: **Other**. Build Command: leave empty. Output Directory:
   leave empty (Vercel serves the root directory as static files).
4. Deploy.

`vercel.json` lives in this folder and is picked up automatically once the root
directory is set. Every push to the repo redeploys.

Even with no build command, Vercel auto-detects serverless functions under
`api/` **inside this root directory** (`src/website/api/`) — a repo-root `api/`
folder would be invisible.

## Newsletter (Resend)

The "Stay in the loop" section on the landing page posts `{email}` to
`/api/subscribe`, which adds the contact to a [Resend](https://resend.com)
Audience. Zero dependencies — plain `fetch` on the Node runtime.

**One-time setup:**

1. Resend dashboard → **Audiences** → create an audience, copy its ID.
2. **API Keys** → create a key with full access to that audience.
3. Vercel → Project → Settings → **Environment Variables**: add
   `RESEND_API_KEY` and `RESEND_AUDIENCE_ID`, enabled for Production, Preview
   and Development (so `vercel env pull` works).

Domain verification is **not** needed to collect contacts — only later, to send
broadcasts from a `@protocol0.live` address. Broadcasts are written and sent
manually from the Resend dashboard.

**Behavior:** invalid emails get a 400; a hidden honeypot field (`company`)
silently drops bots; an already-subscribed email (Resend 409) is treated as
success. There is no rate limiting — if spam ever becomes a problem, add a
KV-backed limiter (e.g. Upstash) in front of the Resend call.

**Local dev:**

```sh
cd src/website
npx vercel link            # one-time: link this folder to the Vercel project
npx vercel env pull .env   # pull the Development env vars
npx vercel dev             # static files + /api/subscribe on localhost:3000
```

## Editing notes

- **Copy & design** are driven by the design handoff. Tokens and components live
  in `design-system.css` (`:root` + component classes); change tokens there to
  retheme everything at once. See `DESIGN.md` to reuse the system elsewhere (e.g.
  the script's web UI).
- **Docs content** is hand-written from the project's behavior. When the app
  changes (new actions, new endpoints, macOS support), update the relevant page
  in `docs/`.
- The landing page's `Docs` link points at `/docs/`; the GitHub and releases
  links point at the real repo.
- Contact email: `contact@thibaultlebrun.dev`.
