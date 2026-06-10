/**
 * @protocol0/extension-sdk — the implementation (layer 2).
 *
 * Optional sugar over the HTTP contract documented in
 * docs/integrations/third-party-extensions.md. A third-party Ableton extension
 * can integrate with Protocol0 WITHOUT this lib by implementing the contract by
 * hand — this file just removes the boilerplate (server, /openapi.json,
 * register/unregister, crash-safety).
 *
 * Design note — the registerCommand trap: a context-menu command receives a
 * selection Handle; a keyboard-triggered action does not. This lib therefore
 * exposes a dedicated `actions` map for context-free, keyboard-bindable actions
 * and deliberately does NOT auto-expose the host's context-menu commands.
 */
/** A JSON-schema-ish param type Protocol0 understands. */
type ParamType = "string" | "integer" | "number" | "boolean";
/** One keyboard-bindable action. */
export interface ActionDef {
    /** One-line summary → becomes the action description/label in the keymapper. */
    summary: string;
    /** Declared params (name → type). Required by default; mark optional explicitly. */
    params?: Record<string, ParamType | {
        type: ParamType;
        required?: boolean;
    }>;
    /** Your logic. `args` is the decoded JSON body keyed by param name. */
    handler: (args: Record<string, unknown>) => void | Promise<void>;
}
export interface ExposeOptions {
    /** Unique extension name; namespaces your actions as /action/<name>/<action>. */
    name: string;
    /** The actions to expose for keyboard binding. */
    actions: Record<string, ActionDef>;
    /** Preferred port; falls back to an ephemeral port if taken. Default 0 (ephemeral). */
    port?: number;
}
/** Handle returned by exposeToProtocol0 so the caller can tear down on shutdown. */
export interface Protocol0Handle {
    readonly url: string;
    close(): Promise<void>;
}
/**
 * Start the HTTP server, serve /openapi.json + the action handlers, and announce
 * this extension to Protocol0's agent. Call once from your extension's activate().
 */
export declare function exposeToProtocol0(opts: ExposeOptions): Promise<Protocol0Handle>;
export {};
