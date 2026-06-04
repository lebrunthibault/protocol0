/**
 * Example: how a third-party extension would use @protocol0/sdk (layer 2).
 *
 * This is the whole integration — start to finish. Compare with implementing the
 * HTTP contract by hand (docs/integrations/third-party-extensions.md): the lib
 * collapses the server, /openapi.json, register/unregister and crash-safety into
 * one call, so the integrator writes ONLY their action logic.
 *
 * Sketch only — not built, not wired (see protocol0.ts header).
 */

import { initialize, type ActivationContext } from "@ableton-extensions/sdk";
import { exposeToProtocol0, type Protocol0Handle } from "./protocol0";

let p0: Protocol0Handle | undefined;

export async function activate(activation: ActivationContext) {
  const context = initialize(activation, "1.0.0");

  // The integrator declares context-free, keyboard-bindable actions. No Handle is
  // involved (that's the registerCommand trap) — these run from a global hotkey.
  p0 = await exposeToProtocol0({
    name: "my-extension",
    actions: {
      randomize_colors: {
        summary: "Randomize the colors of all clips in the set.",
        params: { seed: "integer" },
        handler: async ({ seed }) => {
          await context.withinTransaction(() => {
            // ...iterate tracks/clips and recolor using `seed`...
            console.log(`recoloring with seed=${String(seed)}`);
          });
        },
      },
      mute_all: {
        summary: "Mute every track.",
        // no params → no requestBody in the generated /openapi.json
        handler: () => {
          for (const track of context.application.song.tracks) {
            // ...track.mute = true (illustrative)...
            void track;
          }
        },
      },
    },
  });

  // Now the user can bind any key to "Randomize Colors" / "Mute All" in Protocol0.
}

// The host has no formal deactivate hook; tear down on process exit.
process.on("SIGTERM", () => {
  void p0?.close().finally(() => process.exit(0));
});
