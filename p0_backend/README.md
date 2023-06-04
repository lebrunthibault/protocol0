# Protocol0 control surface script backend

This repo is the backend of ([Ableton control surface script](https://github.com/lebrunthibault/Protocol0-Ableton-Surface-Script))

I created it because the python environment in the control surface script executes in ableton and is limited in several
ways
(cannot use threading, asyncio, python3, a bunch of system libraries etc ...)

This repo has none of these limitations and exposes an API to the protocol0 script 
while also being able to do the opposite : 
calling the script by dispatching script RPC commands.

- This backend is clearly niche and also Windows specific (some library code is relative to windows and keyboard management))

> legend:
>- script: the ableton control surface script
>- backend: this repo

## Installation

`make bootstrap`

### Install other dependencies
- [Open Api generator](https://openapi-generator.tech/docs/installation/) to generate the sdk for the backend api
- [AHK](https://www.autohotkey.com/)

### Generate the backend api client
- install java
- `make sdk`

### Set up the midi ports
- Create LoopMidi virtual ports (P0_IN and P0_OUT)
- configure ableton midi as so :
    <img width="260px" src="https://raw.githubusercontent.com/lebrunthibault/Protocol-0-backend/master/doc/img/ableton_midi_config.PNG?sanitize=true" alt="ableton screenshot">

  
### Makefile
- most commands I run from the terminal are gathered here (starting processes, sdk generation, tests and lint)

### Start the backend server
- `make celery`
- `make midi_server`
- `make http_server`

## Components

### ./api

The user facing APIs for the backend

#### ./api/midi_server
A MIDI server exposing the backend API for consumption by the [control surface script](https://github.com/lebrunthibault/Protocol0-Ableton-Surface-Script)
(the script communicates only via MIDI)

Also includes client code for
- accessing the backend API from the script (python2)
- accessing the backend API from python3 (needed to access the Backend from outside the MIDI server, see http_server below)
  - NB : due to windows limitations on MIDI ports (only one connection possible), "talking" to the script is only possible from the midi server
  - That means that sending a command to the script from outside the server, we first need to call the server that will forward the command to the script.
- Calling the script from the backend (server push)
  
NB : the backend API is not exposed in the same way as the script API (this should be fixed)
- The backend clients are generated using open API tools. They generate a python client that has a method per exposed backend `Route` method.
  It's nice to do code generation but replacing the `Route` class by Command objects would be simpler
- The script client uses RPC and dispatches script Command objects over MIDI. 
  It's simpler (even though it creates a hard dependency on the script. but it's ok they are both on the same machine)
  
#### ./api/http_server
I've also set up a minimal http server using FastAPI.
This server is there as a gateway to the midi server, for clients that cannot use MIDI
It serves two clients :
- ahk hotkeys : that's because hitting an API is considerably faster than executing scripts with python.
- my streamdeck. The server pushes song state changes to the stream deck via a websocket endpoint

It's run independently of the midi server. 

### ./gui
Code used to create notifications and dialog boxes that are displayed on top of ableton interface.
Windows are displayed in celery tasks.
  
### ./lib
This is the common backend library used by most backend components.


### ./scripts

#### ahk
I've setup a few [Auto Hotkey](https://www.autohotkey.com/) (AHK) hotkeys. Mostly they are a way to call the backend.

Doing hotkey detection in python didn't work as well, that's why I kept this (windows) dependency.

In the 'standard' way of executing backend code via ahk, we usually follow these steps :
- hotkey pressed
- ahk dispatches a GET request to the p0 http api
- the backend code executes, potentially forwarding the command to the script
- In this last case the ahk will in the end trigger a script command (like 'ToggleSceneLoopCommand')

## Development
- format, lint and test using turborepo and package.json
