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
- The script also acts as an HTTP client: it can call out to a python
  fastapi backend ([p0_backend](https://github.com/lebrunthibault/protocol0/tree/main/p0_backend))
  running on the same machine, for things the Ableton-bundled python
  interpreter can't do (spawn processes, win32 apis, mouse/keyboard, …).

## The backend

This script executes in the context of ableton's bundled python interpreter, like any script. Some things are not
possible in this environment like accessing win32apis (keyboard, mouse ..)
So I've set up a separate HTTP backend in python that the script can call.

## Installation

`make bootstrap`

### Install the script in your remote scripts folder

- `make install_script`

> This generates a simple midi remote script importing the control surface
> from the [protocol0](https://pypi.org/project/protocol0/) pypi library.

### Install the backend

- follow the README install section of the [backend](https://github.com/lebrunthibault/protocol0/tree/main/p0_backend).

## Development

I've written a technical doc that details important parts of the script object model and techniques. Also, a few remote
scripts concepts are
explained. [see this article](https://lebrunthibault.github.io/post/music/protocol0/p0-technical-overview/) (might be a bit
outdated)

I've been using DDD concepts to structure the script with a single central domain folder

### Coding tools and tests

- `npm run lint`
- `npm run test`
