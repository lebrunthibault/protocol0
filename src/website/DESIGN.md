# Protocol 0 — design system

The single source of truth is [`design-system.css`](./design-system.css). It is
**self-contained**: the only external dependency is two Google fonts. Copy that file
(link it or inline its contents), load the fonts, and you have the full Protocol 0 look —
the same tokens and components the website uses.

This doc exists so that *"copy the website's design"* is a one-file operation: the charte
graphique (below) and the component catalog are extracted into tokens and reusable classes.

## How to reuse it (e.g. the script's web UI)

1. Copy `design-system.css` verbatim into the target surface, or inline its contents in a
   `<style>` block (the script serves its UI as an inline HTML string from Python, so inline
   it there).
2. Load the two fonts in the `<head>`:

   ```html
   <link rel="preconnect" href="https://fonts.googleapis.com">
   <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
   <link href="https://fonts.googleapis.com/css2?family=Schibsted+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
   ```

3. Use the component classes below. Done — no other dependency.

**Golden rule:** never hardcode a hex or px in a component. Always go through a token
(`var(--…)`). Dark theme, blue accent (`--accent`), monospace for key combos / code /
technical values.

## Charte graphique (tokens)

All tokens are CSS custom properties on `:root` in `design-system.css`.

### Colors

| Token | Value | Usage |
| --- | --- | --- |
| `--bg` | `#000000` | Page background |
| `--panel` | `#0b0c0e` | Card / surface base |
| `--panel-2` | `#101113` | Lighter surface, input fields |
| `--line` | `rgba(255,255,255,.09)` | Default borders / dividers |
| `--line-strong` | `rgba(255,255,255,.15)` | Emphasized borders |
| `--text` | `#f3f4f6` | Primary text |
| `--text-soft` | `#c2c4ca` | Prose body text |
| `--muted` | `#85878d` | Secondary text, labels |
| `--muted-2` | `#5e6066` | Tertiary text, captions |
| `--accent` | `#4d9fff` | Brand blue — links, focus, highlights |
| `--accent-soft` | `#9cc8ff` | Softer accent (code text, icons) |
| `--accent-bg` | `rgba(77,159,255,.08)` | Tinted fill behind code / icons / notes |
| `--accent-line` | `rgba(77,159,255,.18)` | Tinted accent borders |
| `--warn` / `--warn-bg` / `--warn-line` | amber set | Warning callouts |
| `--ok` | `#5fd08a` | Success messages |
| `--err` | `#ff6b6b` | Error messages |

### Typography

| Token | Value | Usage |
| --- | --- | --- |
| `--font-sans` | `'Schibsted Grotesk', system-ui, sans-serif` | All UI text |
| `--font-mono` | `'JetBrains Mono', monospace` | Combos, code, technical values |
| `--fs-xs … --fs-2xl` | `11 / 13 / 14 / 15 / 17 / 18 / 24 px` | Size scale |
| `--fs-h1` / `--fs-h2` / `--fs-doc-h1` | fluid `clamp()` | Headings |
| `--fw-regular / --fw-medium / --fw-semibold` | `400 / 500 / 600` | Weights |
| `--lh-tight / --lh-snug / --lh-relaxed` | `1.1 / 1.5 / 1.65` | Line heights |
| `--ls-tight / --ls-snug / --ls-wide` | `-0.025em / -0.01em / .04em` | Letter spacing |

### Spacing — base-4 scale

`--space-1`…`--space-9` = `4 / 8 / 12 / 16 / 24 / 32 / 40 / 56 / 70 px`.

### Radii

`--radius-sm` `5px` · `--radius-md` `9px` (buttons, inputs) · `--radius-lg` `12px`
(callouts, code blocks) · `--radius-xl` `20px` (cards) · `--radius-pill` `100px`.

### Shadows & transitions

`--shadow-key`, `--shadow-key-lit`, `--shadow-dot`, `--shadow-glow` ·
`--t-fast` `.15s` · `--t` `.2s` · `--t-slow` `.3s`.

## Components

### Card — `.card` + modifiers

```html
<div class="card">…</div>                          <!-- gradient panel + top glow -->
<div class="card card--flat">…</div>               <!-- flat panel, no gradient/glow -->
<div class="card card--center">…</div>             <!-- centered text -->
<div class="card card--download card--center">…</div> <!-- large pad + radial halo -->
<a class="card card--compact" href="…">…</a>       <!-- compact tile, lifts on hover -->
```

Compose modifiers freely. Card content is automatically lifted above the glow layers.

### Buttons — `.btn`

```html
<a class="btn btn-primary">Download</a>   <!-- white, primary action -->
<a class="btn btn-ghost">View on GitHub</a> <!-- subtle, secondary -->
```

### Eyebrow / badge / label

```html
<span class="eyebrow"><span class="badge">Ableton 12</span> · Windows</span>
<div class="label-accent">Documentation</div>   <!-- small accent caption -->
```

### Callouts — `.note` / `.warn`

```html
<div class="note"><svg class="ic">…</svg><p>Informational note.</p></div>
<div class="warn"><svg class="ic">…</svg><p>Watch out for this.</p></div>
```

### Table — `.table`

```html
<table class="table">
  <thead><tr><th>Combo</th><th>Action</th></tr></thead>
  <tbody><tr><td>ctrl+shift+p</td><td>load_device</td></tr></tbody>
</table>
```

(Docs prose tables under `.docs-article` are styled identically without the class.)

### Code

`<code>inline</code>` and `<pre><code>block</code></pre>` are styled out of the box.

### Form controls (for the script's web UI)

```html
<div class="field">
  <label class="field-label" for="action">Action</label>
  <select class="select" id="action">…</select>
</div>

<div class="field">
  <label class="field-label">Combo</label>
  <span class="capture" tabindex="0">click &amp; press…</span>  <!-- mono combo capture box -->
</div>

<input class="input" placeholder="value">

<div class="msg msg--ok">Added.</div>
<div class="msg msg--err">Capture a combo first.</div>
```

Use `.btn`/`.btn-primary` for form buttons. Inputs share the same focus ring (`--accent` +
`--accent-bg` glow).
