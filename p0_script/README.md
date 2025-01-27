# Protocol0 Control Surface Script for Ableton

Protocol0 is a control surface script for Ableton Live 11+

It is focused on working in session view and usually acts on the selected track or scene. 

I've been specifically working on making the session recording more powerful and more adapted to my workflow.

The scripts react to a set of midi note and cc messages. I'm currently triggering those using a Faderfox EC4.
> This script is definitely a "working on my machine" script and is not generic to any layout / usage.
> It should be interesting for a remote script dev though.

## Architecture
- The script wraps a good part of the Live python api and adds its own logic on top
- The script is accessible directly via midi cc and note messages. Originally I was reaching it only using my Faderfox EC4
- The script can be reached via any MIDI port, so I've been using Loop Midi to send midi into the script 
from python running on my local machine.
- I do it by having a python fastapi server running locally
- The server exposes a http api that work in 2 ways (bidirectional) :
  - Be a backend to the script for tasks that need to run in a full python environment (call windows apis etc ..)
  - Expose the api to the outside and translate calls into midi messages (I call them commands)
- At the moment I consume the server api points in 3 ways (all the code is present in the monorepo):
  - via ahk shortcuts, so I can create custom shortcuts linked to the script ([p0_ahk](https://github.com/lebrunthibault/protocol0/tree/main/p0_ahk))
  - via my Elgato stream deck ([p0_stream_deck](https://github.com/lebrunthibault/protocol0/tree/main/p0_stream_deck))
  - via a vue.js web app running locally ([p0_web](https://github.com/lebrunthibault/protocol0/tree/main/p0_web))

## Features

Used to be a session view tool for recording stuff like external synth / audio, scrolling scenes, duplicating clips, freezing / flattening tracks..
It's not anymore, and I removed a few of the more complex features. 
<br><br>

## The backend

This script executes in the context of ableton's bundled python interpreter, like any script. Some things are not
possible in this environment like spawning processes or accessing win32apis (keyboard, mouse ..)
A simple example : clicking on a device show button is not possible from a "normal" script. To make this kind of thing
possible I've created a backend that you can find in [here](https://github.com/lebrunthibault/protocol0/tree/main/p0_backend).

NB : quite some features are not implemented in the API (freezing, flattening, cropping .. but also dragging in or out tracks etc ..).
All of this is implemented using the backend sometime leveraging wild mouse clicks.

The backend is exposing its api over midi, and I'm using loopMidi virtual ports to communicate with it.

> Without setting up the backend (might not be straightforward) the script will only partially work.

> As it's not possible to listen to multiple midi ports from a surface script I'm using a "proxy" surface script that forwards messages
> from my backend on its port to the main script. See `make install_scripts`
> The same purpose would be achievable my external midi routing using e.g. midi ox.

## Installation

`make bootstrap`

### Install the script in your remote scripts folder

- `make install_script`

Will install two scripts
- **p0**: the main script
- **p0_midi**: a proxy script that forwards input midi messages to the main script (overcomes the windows single midi input limitation)

> These commands will generate two simple midi remote scripts
> importing control surfaces from the [protocol0](https://pypi.org/project/protocol0/) pypi library.

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
