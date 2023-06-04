# Stream Deck Plugin for [Ableton Protocol0 Surface Script](https://github.com/lebrunthibault/Protocol0-Ableton-Surface-Script)

- A stream deck plugin that interfaces with my python control surface script for Ableton
- Built with the [Stream Deck SDK](https://developer.elgato.com/documentation/stream-deck/sdk/overview/#sdk), Javascript version
- Connected to the surface script via the [protocol0 backend](https://github.com/lebrunthibault/Protocol0-backend) websocket server
- The ableton set is synchronized in realtime via the AbletonSet and ServerState objects pushed from the websocket server
- Introduced the concept of action slot to have a better display control over a range of buttons 
- Written in Typescript and bundled with Vite


