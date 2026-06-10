/**
 * @protocol0/extension-sdk — public entry point.
 *
 * One call (`exposeToProtocol0`) turns an Ableton Extensions SDK extension into a
 * Protocol0-bindable surface: it starts the HTTP server, serves `/openapi.json` and
 * your action handlers, registers/unregisters with the Protocol0 agent on :9010, and
 * installs the crash nets the Extension Host needs. It is optional sugar over the
 * HTTP+JSON contract documented at docs/integrations/third-party-extensions.md — you
 * can implement that contract by hand in any language; this just removes the boilerplate.
 */
export { exposeToProtocol0 } from "./protocol0.js";
