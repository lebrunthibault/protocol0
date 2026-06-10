/**
 * Reference Protocol0-compatible extension.
 *
 * This is the end-to-end test of the integration: it declares a couple of context-free,
 * keyboard-bindable actions and hands them to `@protocol0/extension-sdk`, which starts the
 * HTTP server, serves /openapi.json + the handlers, and announces the extension to the
 * Protocol0 agent on :9010. Once activated, the actions show up in the Protocol0 keymapper
 * (GET http://127.0.0.1:9010/api/actions) and can be bound to any key combo.
 *
 * Compare with the previous spike (a hand-rolled http server + runtime.json): the SDK
 * collapses all of that — server, openapi, register/unregister, crash-safety — into one call,
 * so the integrator writes ONLY their action logic.
 */

import { initialize, type ActivationContext } from "@ableton-extensions/sdk";
import { exposeToProtocol0, type Protocol0Handle } from "@protocol0/extension-sdk";
import bundledInterface from "../ui/interface.html";

let p0: Protocol0Handle | undefined;

export function activate(activation: ActivationContext) {
  const context = initialize(activation, "1.0.0");

  // Demo webview (context-menu) — orthogonal to Protocol0, kept to show the SDK context works.
  context.commands.registerCommand("protocol-0.showDialog", () => {
    const url = `data:text/html,${encodeURIComponent(bundledInterface)}`;
    context.ui.showModalDialog(url, 320, 160).then((result) => {
      console.log(`Dialog closed with: ${result}`);
    });
  });
  context.ui.registerContextMenuAction("AudioClip", "Open protocol-0", "protocol-0.showDialog");

  // Insert a built-in Live device by name on the first track, as one undo step.
  async function loadDevice(name: string): Promise<void> {
    const track = context.application.song.tracks[0];
    if (!track) {
      console.warn("[protocol-0] load_device: no track in set");
      return;
    }
    await context.withinTransaction(() => track.insertDevice(name, track.devices.length));
    console.log(`[protocol-0] inserted "${name}" on track "${track.name}"`);
  }

  // Declare the keyboard-bindable actions. No selection Handle is involved (the registerCommand
  // trap) — these run from a global hotkey, with args coming from the keymapper binding.
  void exposeToProtocol0({
    name: "protocol-0",
    actions: {
      load_device: {
        summary: "Load a built-in device by name onto the first track.",
        params: { name: "string" },
        handler: async ({ name }) => {
          await loadDevice(String(name ?? ""));
        },
      },
      ping: {
        summary: "No-op action that just logs — proves keyboard binding end-to-end.",
        handler: () => {
          console.log("[protocol-0] ping");
        },
      },
    },
  }).then((handle) => {
    p0 = handle;
    console.log(`[protocol-0] exposed to Protocol0 on ${handle.url}`);
  });

  // The host has no formal deactivate hook; unregister + close the server on process exit.
  process.on("SIGTERM", () => {
    void p0?.close().finally(() => process.exit(0));
  });
}
