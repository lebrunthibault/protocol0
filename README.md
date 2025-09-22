# Protocol0

Protocol0 is a control surface script (aka remote script) for Ableton Live

It's a set of tools for supercharging my live and production workflow in session view.
It's complicated and sometimes useful.

## Requirements
- [Ableton Live 12+](https://www.ableton.com/fr/live/)
- Python 3.7+

## Organisation

I've split the project into different modules :
- [A remote script](https://github.com/lebrunthibault/protocol0/tree/main/p0_script) 
   that is going to be installed in the ableton remote scripts folder and do most of the job
- [A midi and http backend](https://github.com/lebrunthibault/protocol0/tree/main/p0_backend) that makes it possible
  to do things not available in the ableton live python environment and also exposes a http api
  that can be reached from outside (by e.g. ahk keyboard shortcuts or non-midi controllers like a streamdeck)
- [A sdk generator](https://github.com/lebrunthibault/protocol0/tree/main/p0_sdk) : generates a python sdk for consuming the api (overkill and nerdy)
- [A web frontend](https://github.com/lebrunthibault/protocol0/tree/main/p0_web) : a simple web app
  where the control surface script actions can be triggered from the browser. In case you don't have a midi controller at hand  (legacy)
- [A stream deck plugin](https://github.com/lebrunthibault/protocol0/tree/main/p0_stream_deck): an integration with elgato stream deck (legacy)
- [An ahk script](https://github.com/lebrunthibault/protocol0/tree/main/p0_ahk): keyboard shortcuts for controlling the script (by calling the http api)
