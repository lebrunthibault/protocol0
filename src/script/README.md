# Protocol0 Control Surface Script for Ableton

Protocol0 is a control surface script for Ableton Live 11+

It is as of today a minimal set of helpful tools for Ableton in particular:
- quick track selection by name (e.g. "kick", "snare", "bass", "vocal", etc.)
- fast device loading (possible to add custom shortcuts to load your most used devices)

The script can be used either with a midi controller (I'm using a Faderfox EC4) or with keyboard shortcuts (using AHK to trigger http calls to the script).

## Architecture
- The script answers to midi cc and note messages. Originally I was reaching it only using my Faderfox EC4
- The script also exposes its own HTTP server so anything on the machine can drive it without going
  through MIDI — typically keyboard shortcuts (AHK) that hit a URL like
  `http://127.0.0.1:9000/track/select?name=kick`.
- The script also acts as an HTTP client (via `BackendClient`): it can call out to
  a local HTTP backend for things the Ableton-bundled python interpreter can't do
  (spawn processes, win32 apis, mouse/keyboard, …). That backend has been extracted
  to a separate repository and is currently dormant; the client stays in place for
  if/when it is revived.

## Installation

`make bootstrap`

### Install the script in your remote scripts folder

- `make install_script`

> This generates a simple midi remote script importing the control surface
> from the [protocol0](https://pypi.org/project/protocol0/) pypi library.

## Development

I've written a technical doc that details important parts of the script object model and techniques. Also, a few remote
scripts concepts are
explained. [see this article](https://lebrunthibault.github.io/post/music/protocol0/p0-technical-overview/) (might be a bit
outdated)

I've been using DDD concepts to structure the script with a single central domain folder

### Coding tools and tests

- `npm run lint`
- `npm run test`
