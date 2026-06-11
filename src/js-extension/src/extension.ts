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

let p0: Protocol0Handle | undefined;

export function activate(activation: ActivationContext) {
  const context = initialize(activation, "1.0.0");

  // Declare the keyboard-bindable actions. No selection Handle is involved (the registerCommand
  // trap) — these run from a global hotkey, with args coming from the keymapper binding.
  void exposeToProtocol0({
    name: "protocol0-example", // namespaces actions as /action/protocol0-example/<action>
    actions: {
      load_device: {
        summary: "Load a built-in device by name onto the first track.",
        params: { name: "string" },
        handler: async ({ name }) => {
          const track = context.application.song.tracks[0];
          if (!track) {
            console.warn("[protocol0-example] load_device: no track in set");
            return;
          }
          const deviceName = String(name ?? "");
          await context.withinTransaction(() =>
            track.insertDevice(deviceName, track.devices.length),
          );
          console.log(`[protocol0-example] inserted "${deviceName}" on track "${track.name}"`);
        },
      },
      mute_all: {
        summary: "Mute every track.", // no params → no requestBody in the openapi
        handler: () => {
          context.withinTransaction(() => {
            for (const track of context.application.song.tracks) {
              track.mute = true;
            }
          });
          console.log("[protocol0-example] muted all tracks");
        },
      },
    },
  }).then((handle) => {
    p0 = handle;
    console.log(`[protocol0-example] exposed to Protocol0 on ${handle.url}`);
  });

  // The host has no formal deactivate hook; unregister + close the server on process exit.
  process.on("SIGTERM", () => {
    void p0?.close().finally(() => process.exit(0));
  });
}
