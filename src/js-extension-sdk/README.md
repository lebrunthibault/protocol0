# @protocol0/extension-sdk

[![npm version](https://img.shields.io/npm/v/@protocol0/extension-sdk.svg)](https://www.npmjs.com/package/@protocol0/extension-sdk)
[![license](https://img.shields.io/npm/l/@protocol0/extension-sdk.svg)](https://github.com/lebrunthibault/protocol0/blob/main/LICENSE.md)

Expose your [Ableton Extensions SDK](https://www.ableton.com/) extension's actions to
[Protocol0](https://www.protocol0.live/) keyboard shortcuts — with one call.

Protocol0 runs a global keyboard hook. If your extension announces its actions, the user
can bind any key combo to one of them in the Protocol0 keymapper. When they press the
combo, Protocol0 calls your action over localhost HTTP — even when Ableton is not focused.

This package is **optional sugar** over a plain HTTP + JSON contract
(see [the integration doc](https://github.com/lebrunthibault/protocol0/blob/main/docs/integrations/third-party-extensions.md)).
You can implement that contract by hand in any language; this just removes the boilerplate
(HTTP server, `/openapi.json`, register/unregister, crash-safety).

## Install

```bash
npm install @protocol0/extension-sdk
```

## Usage

Call `exposeToProtocol0` once from your extension's `activate()`:

```ts
import { initialize, type ActivationContext } from "@ableton-extensions/sdk";
import { exposeToProtocol0, type Protocol0Handle } from "@protocol0/extension-sdk";

let p0: Protocol0Handle | undefined;

export function activate(activation: ActivationContext) {
  const context = initialize(activation, "1.0.0");

  void exposeToProtocol0({
    name: "my-extension", // namespaces your actions as /action/my-extension/<action>
    actions: {
      randomize_colors: {
        summary: "Randomize the colors of all clips in the set.",
        params: { seed: "integer" }, // string | integer | number | boolean
        handler: async ({ seed }) => {
          await context.withinTransaction(() => {
            // ...recolor using `seed`...
          });
        },
      },
      mute_all: {
        summary: "Mute every track.", // no params → no requestBody in the openapi
        handler: () => {
          for (const track of context.application.song.tracks) track.mute = true;
        },
      },
    },
  }).then((h) => {
    p0 = h;
  });

  // The host has no formal deactivate hook; tear down on process exit.
  process.on("SIGTERM", () => void p0?.close().finally(() => process.exit(0)));
}
```

That's it. The user can now bind keys to **Randomize Colors** / **Mute All** in Protocol0.

## What it does for you

- Starts an HTTP server on an ephemeral `127.0.0.1` port (override with `port`).
- Serves `GET /openapi.json` (the format Protocol0's catalog parser reads) and
  `POST /action/<name>/<action>` for each handler.
- Registers with the Protocol0 agent (`POST http://localhost:9010/api/extensions/register`)
  on start and unregisters on `close()` / process exit. Registration is idempotent soft
  state — if the agent isn't running yet, it's harmless; re-announce on each `activate()`.
- Installs `uncaughtException` / `unhandledRejection` handlers, because an uncaught error
  **kills the whole Extension Host**.

## The `registerCommand` trap

A context-menu command receives a selection `Handle` (the clicked clip/track). A
**keyboard-triggered** action has no such handle — nothing was clicked. So this SDK exposes
a dedicated `actions` map for context-free, keyboard-bindable actions and deliberately does
**not** auto-expose your context-menu commands.

## API

```ts
exposeToProtocol0(opts: {
  name: string;                        // unique; namespaces /action/<name>/<action>
  actions: Record<string, ActionDef>;  // your keyboard-bindable actions
  port?: number;                       // default 0 (ephemeral)
}): Promise<Protocol0Handle>;          // { url, close() }

interface ActionDef {
  summary: string;                     // one-line label shown in the keymapper
  params?: Record<string, "string" | "integer" | "number" | "boolean"
                        | { type: ...; required?: boolean }>;
  handler: (args: Record<string, unknown>) => void | Promise<void>;
}
```

## License

MIT
