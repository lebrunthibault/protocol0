import { initialize, type ActivationContext } from "@ableton-extensions/sdk";
import * as http from "node:http";
import * as fs from "node:fs";
import * as path from "node:path";
import { URL } from "node:url"; // le host sandbox n'expose pas URL en global

// esbuild inlines this HTML file as a string for production builds.
import bundledInterface from "../ui/interface.html";

// ---------------------------------------------------------------------------
// SPIKE — valider Test A/B/C de l'audit (portage Protocol0 -> Extensions SDK).
//
//   Test A : un http.createServer sur 127.0.0.1 survit-il dans l'Extension Host
//            (sandbox) ? -> GET /api/health.
//   Test B : une action Live (insertDevice natif) marche-t-elle depuis un handler
//            HTTP ? -> POST /api/device/load {name:"Reverb"}. Latence loggée.
//   Test C : le detector existant (qui lit runtime.json / P0_SCRIPT_PORT) peut
//            taper cette extension sans changer son contrat -> on écrit runtime.json
//            au même schéma/au même endroit que le script Python.
//
// Le serveur écoute 9005 (9000 = API du script Python ; 9001 = backend poetry).
// On ne recrée AUCUNE couche objet : object model SDK brut, handles à la demande.
// ---------------------------------------------------------------------------

const SPIKE_VERSION = "spike";
const PREFERRED_PORT = 9005;

// Réplique du contrat du script Python : %APPDATA%\Protocol0\runtime.json
function runtimePath(): string {
  const appData =
    process.env.APPDATA ?? path.join(process.env.USERPROFILE ?? ".", "AppData", "Roaming");
  return path.join(appData, "Protocol0", "runtime.json");
}

function writeRuntime(scriptUrl: string): void {
  const p = runtimePath();
  fs.mkdirSync(path.dirname(p), { recursive: true });
  const tmp = p + ".tmp";
  const payload = { script_url: scriptUrl, pid: process.pid, version: SPIKE_VERSION };
  fs.writeFileSync(tmp, JSON.stringify(payload), "utf-8");
  fs.renameSync(tmp, p); // remplacement atomique
}

function clearRuntime(): void {
  try {
    fs.rmSync(runtimePath(), { force: true });
  } catch {
    /* best effort */
  }
}

export function activate(activation: ActivationContext) {
  const context = initialize(activation, "1.0.0");

  // --- Webview demo (généré par le scaffolder, gardé tel quel) ---------------
  context.commands.registerCommand("protocol-0.showDialog", () => {
    const url = `data:text/html,${encodeURIComponent(bundledInterface)}`;
    context.ui.showModalDialog(url, 320, 160).then((result) => {
      console.log(`Dialog closed with: ${result}`);
    });
  });
  context.ui.registerContextMenuAction("AudioClip", "Open protocol-0", "protocol-0.showDialog");

  // --- Cœur du portage : insérer un device natif sur la 1re track ------------
  // Promesse, résout les handles à la demande (pas de cache d'objet Live).
  async function loadDeviceDirect(name: string): Promise<string> {
    const song = context.application.song;
    const track = song.tracks[0];
    if (!track) return "no track in set";
    // withinTransaction : callback synchrone, mais renvoyer la Promise groupe l'undo.
    await context.withinTransaction(() => track.insertDevice(name, track.devices.length));
    return `inserted "${name}" on track "${track.name}"`;
  }

  // Repli "command" pour le cas où toucher l'object model hors callback de command
  // serait interdit par le host. executeCommand est fire-and-forget côté SDK.
  context.commands.registerCommand("protocol-0.load_device", (...args: unknown[]) => {
    const name = String(args[0] ?? "");
    loadDeviceDirect(name)
      .then((r) => console.log(`[load_device via command] ${r}`))
      .catch((e) => console.error(`[load_device via command] error: ${String(e)}`));
  });

  // --- Serveur HTTP (Test A) -------------------------------------------------
  // Le contrat suit l'API du script Python : routes sous /api, GET en lecture,
  // POST (body JSON) en mutation. La mutation lit `name` dans le body POST ;
  // `?via=command` reste un query param de debug.
  const server = http.createServer((req, res) => {
    const json = (code: number, body: unknown) => {
      res.writeHead(code, { "content-type": "application/json" });
      res.end(JSON.stringify(body));
    };

    let url: URL;
    try {
      url = new URL(req.url ?? "/", "http://127.0.0.1");
    } catch (e) {
      // ne JAMAIS laisser une exception remonter : elle tue l'Extension Host.
      console.error(`[http] bad request: ${String(e)}`);
      return json(400, { ok: false, error: "bad request" });
    }
    const via = url.searchParams.get("via"); // "command" pour forcer le repli

    if (url.pathname === "/api/health" && req.method === "GET") {
      // Test A : si ça répond depuis l'extérieur, l'écoute survit au sandbox.
      return json(200, { ok: true, version: SPIKE_VERSION });
    }

    if (url.pathname === "/api/device/load" && req.method === "POST") {
      // Lit le body JSON {name}. On bufferise — les bodies sont minuscules.
      let raw = "";
      req.on("data", (chunk) => (raw += chunk));
      req.on("end", () => {
        let name = "";
        try {
          name = String((JSON.parse(raw || "{}") as { name?: unknown }).name ?? "");
        } catch {
          return json(400, { ok: false, error: "invalid JSON body" });
        }
        if (!name) return json(400, { ok: false, error: "missing 'name'" });
        const t0 = process.hrtime.bigint();
        if (via === "command") {
          // chemin repli : passe par le bus de commands du SDK
          context.commands.executeCommand("protocol-0.load_device", name);
          return json(202, { ok: true, path: "command", note: "fire-and-forget, voir logs" });
        }
        // chemin direct : object model touché depuis l'event loop Node
        loadDeviceDirect(name)
          .then((detail) => {
            const ms = Number(process.hrtime.bigint() - t0) / 1e6;
            console.log(`[load_device direct] ${detail} (${ms.toFixed(1)} ms)`);
            json(200, { ok: true, path: "direct", detail, latency_ms: Number(ms.toFixed(1)) });
          })
          .catch((e) => {
            console.error(`[load_device direct] error: ${String(e)}`);
            json(500, { ok: false, path: "direct", error: String(e) });
          });
      });
      return;
    }

    if (url.pathname === "/api/track/select" && req.method === "POST") {
      // Pas d'API de sélection dans le SDK 1.0.0-beta.0 -> stub (conforme audit).
      console.warn("select_track not implemented — no SDK selection API");
      return json(501, { ok: false, error: "not implemented — no SDK selection API" });
    }

    json(404, { ok: false, error: "not found" });
  });

  server.on("error", (e) => {
    if ((e as NodeJS.ErrnoException).code === "EADDRINUSE") {
      console.warn(`port ${PREFERRED_PORT} busy — retrying on an ephemeral port`);
      server.listen(0, "127.0.0.1");
    } else {
      console.error(`http server error: ${String(e)}`);
    }
  });

  server.listen(PREFERRED_PORT, "127.0.0.1", () => {
    const addr = server.address();
    const port = typeof addr === "object" && addr ? addr.port : PREFERRED_PORT;
    const scriptUrl = `http://127.0.0.1:${port}`;
    writeRuntime(scriptUrl); // Test C : detector lit ça (ou P0_SCRIPT_PORT)
    console.log(`[spike] HTTP listening on ${scriptUrl} — runtime.json written`);
  });

  // Filet de sécurité spike : logger plutôt que laisser le host crasher.
  process.on("uncaughtException", (e) => console.error(`[uncaughtException] ${String(e)}`));
  process.on("unhandledRejection", (e) => console.error(`[unhandledRejection] ${String(e)}`));

  // L'extension meurt avec Live ; on nettoie runtime.json au shutdown du host.
  process.on("exit", clearRuntime);
  process.on("SIGTERM", () => {
    clearRuntime();
    process.exit(0);
  });
}
