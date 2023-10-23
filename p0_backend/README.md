# Protocol0 control surface script backend

This repo is the backend of ([Ableton control surface script](https://github.com/lebrunthibault/Protocol0-Ableton-Surface-Script))

I created it because the python environment in the control surface script executes in ableton and is limited in several
ways
(cannot use threading, asyncio, python3, a bunch of system libraries etc ...)

This repo has none of these limitations and exposes an API to the protocol0 script 
while also being able to do the opposite : 
calling the script by dispatching script RPC commands.

- This backend is Windows specific (some library code is relative to windows and keyboard management))

## Installation

`make bootstrap`

### Set up the midi ports
- Create LoopMidi virtual ports (P0_IN and P0_OUT)
- configure ableton midi as so :
    <img width="260px" src="https://raw.githubusercontent.com/lebrunthibault/Protocol-0-backend/master/doc/img/ableton_midi_config.PNG?sanitize=true" alt="ableton screenshot">

  
### Makefile
- most commands I run from the terminal are gathered here (starting processes, sdk generation, tests and lint)

### Start the backend
- `make midi_server`
- `make http_server`

## API

#### HTTP
A fastapi exposing the backend API for consumption by the [control surface script](https://github.com/lebrunthibault/Protocol0-Ableton-Surface-Script)

It serves several clients :
- ahk hotkeys : that's because hitting an API is considerably faster than executing scripts with python.
- my streamdeck. The server pushes song state changes to the stream deck via a websocket endpoint
- p0_web : the small protocol0 control web app 



#### Midi server
A gateway MIDI server that allows the backend to be reached via midi (from the control surface script) that doesn't handle well http.

