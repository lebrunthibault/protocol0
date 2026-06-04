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
