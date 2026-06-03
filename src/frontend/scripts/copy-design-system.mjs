// Copie le design system depuis sa source unique (src/website/design-system.css)
// vers src/frontend/src/styles/ (gitignoré) avant chaque build/dev. Évite la dérive :
// le CSS n'est édité qu'à un seul endroit. Copie aussi le favicon partagé.
import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(here, "..", "..", ".."); // src/frontend/scripts -> repo root
const websiteDir = resolve(repoRoot, "src", "website");
const frontendDir = resolve(here, "..");

function copy(from, to) {
  mkdirSync(dirname(to), { recursive: true });
  copyFileSync(from, to);
  console.log(`copied ${from} -> ${to}`);
}

copy(
  resolve(websiteDir, "design-system.css"),
  resolve(frontendDir, "src", "styles", "design-system.css"),
);
copy(resolve(websiteDir, "favicon.svg"), resolve(frontendDir, "public", "favicon.svg"));
