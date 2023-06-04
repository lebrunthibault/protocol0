# Protocol0

Protocol0 is a control surface script project for Ableton Live (tested on 11 and 10)

It is a "selected track control" like
script focused on working in session view. 

I've been specifically working on making the session recording more powerful and more adapted to my workflow.
It has a focus on :
- Recording external synths (both midi and audio) in a smart way
- Being able to export / import sub tracks so as to always work on flattened audio track with the possibility to recall the base (midi track) at a button push.

## Organisation

I've split the project into different modules :
- [A control surface remote script](https://github.com/lebrunthibault/protocol0/tree/main/p0_script) 
   that is going to be installed in the ableton remote scripts folder and do most of the job
- [A midi and http backend](https://github.com/lebrunthibault/protocol0/tree/main/p0_backend) that makes it possible
  to do things not available in the ableton live python environment and as well exposes a http api
  that can be triggered by e.g. ahk keyboard shortcuts or other controllers (like a streamdeck)
- [A sdk generator](https://github.com/lebrunthibault/protocol0/tree/main/p0_sdk) : generates a python sdk for consuming the api
- [A web frontend](https://github.com/lebrunthibault/protocol0/tree/main/p0_web) : a simple web app
  where the control surface script actions can be triggered from the browser. In case you don't have a midi controller at hand.
- [A stream deck plugin](https://github.com/lebrunthibault/protocol0/tree/main/p0_stream_deck): an integration with elgato stream deck
