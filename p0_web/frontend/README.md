# protocol0_web

web frontend to the protocol0 api.
Used to reach protocol0 script inside ableton.

The project has 2 goals :
- Be able to reach the script using its available commands
- Display a set explorer where I can:
  - Explore my sets by category, by date or by rate
  - Listen to a set wav file if any
  - Display metadata about the scenes, tracks and devices used in the set (metadata exported by the script)
  - Rate a set
  - Tag the set in two ways
  - Add a comment to a set
  - Archive and soft delete a set

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Type-Check, Compile and Minify for Production

```sh
npm run build
```

### Lint with [ESLint](https://eslint.org/)

```sh
npm run lint
```
