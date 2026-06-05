# Explorer Starlight (thème black) pour le site de docs

**Statut : exploration / pas prioritaire.** Pas encore d'utilisateurs — c'est un
« faire plus pro sur la doc » à reconsidérer quand les docs grossiront, pas un
chantier à lancer maintenant.

## Le sujet

Aujourd'hui le site (`src/website/`) est **zéro build** : HTML + CSS + vanilla JS,
avec un design system maison (`design-system.css`, charte Mirai dark, accent
`#4d9fff`, `Schibsted Grotesk` + `JetBrains Mono`) réutilisé aussi par l'UI web du
script (cf. `src/website/DESIGN.md`). Les docs sont 5 pages HTML écrites à la main
(`docs/index.html`, `installation.html`, `shortcuts.html`, `http-api.html`,
`faq.html`).

Idée à évaluer : [`starlight-theme-black`](https://github.com/adrian-ub/starlight-theme-black),
un thème pour **Astro Starlight** inspiré du look « shadcn docs » (dark, sobre,
pro). C'est un **plugin Starlight** → impose Astro + Starlight + un build step.

## Verdict de compatibilité

Compatible avec une landing custom, mais c'est un **changement d'architecture**
(introduction d'Astro + build), pas un simple ajout. La landing peut être
préservée.

Deux façons de cohabiter :

1. **Landing custom + docs Starlight, même domaine (recommandé le jour venu).**
   - `/` → landing custom (page Astro statique ou HTML servi à côté, hors layout
     Starlight)
   - `/docs/**` → Starlight + thème black
   - Se déploie pareil sur Vercel.

2. **Deux déploiements.** Landing inchangée sur `protocol0.live`, docs Starlight
   sur `docs.protocol0.live`. Plus simple à démarrer, mais deux design systems à
   maintenir + un sous-domaine.

## Gains vs coûts

**Gains** : sidebar/nav auto, recherche full-text (Pagefind), TOC, dark/light,
versionning, look pro immédiat, docs en MDX au lieu de HTML à la main.

**Coûts** :
- Introduit Astro + un build step dans un projet qui n'en a **aucun** aujourd'hui
  (le « zéro build » est un choix explicite du README actuel).
- Le design system maison ne s'applique plus aux docs telles quelles. Le thème a
  sa propre charte ; il faudrait l'accepter ou le re-tokeniser vers `#4d9fff` /
  Schibsted Grotesk / JetBrains Mono (Starlight le permet via custom CSS, mais
  c'est du boulot).
- Migration manuelle des 5 pages HTML → MDX.

## Déclencheur

Reconsidérer quand la recherche full-text et la nav auto manqueront vraiment —
c'est-à-dire quand les docs auront assez grossi. Pas avant. Si c'est lancé, viser
l'**option 1** pour ne casser ni la landing ni le domaine.
