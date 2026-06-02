# Contributing to Protocol0

Thanks for taking the time to look at Protocol0. It's a young, single-author
project, so the process here is deliberately light.

## Reporting bugs

The fastest way to help. A good report includes:

- **Your environment** — OS version, Ableton Live version, and the Protocol0
  version (see [`VERSION`](VERSION)).
- **Logs** — Protocol0 writes rotating logs to `%APPDATA%\Protocol0\logs\`
  (e.g. `detector.log`). Attach the relevant tail, ideally captured right after
  you reproduced the issue.
- **Steps to reproduce** — what you did, what you expected, what happened
  instead. A precise sequence beats a paragraph of description.

Open an issue with that and we have something to work from.

## Running it locally

Protocol0 is a monorepo with three surfaces under `src/`: the **remote
script** (runs inside Ableton), the **detector**, and the **backend**. From the
repo root:

- **Detector** — `make detector`.
- **Backend** — `make backend`.
- **Remote script** — install it into Ableton's MIDI Remote Scripts folder:

  ```sh
  cd src/script
  make bootstrap        # pyenv local 3.11 + poetry install
  make install_script   # copies the script into Ableton, wires up the source dir
  ```

  Then (re)start Ableton Live and select Protocol_0 as a Control Surface.

- **Config UI** — once the script is running, the shortcut-configuration page
  is served by the script itself at <http://127.0.0.1:9000/shortcuts>.
- **Logs** — `%APPDATA%\Protocol0\logs\` (also `make logs` to tail them live).

## Commits

Commit messages should follow the [Conventional Commits](https://www.conventionalcommits.org)
specification and be in lower case.

Use a **scope** in the subject — the part of Protocol0 the commit affects.
Typically this is one of the three surfaces (`script`, `detector`, `backend`),
but it can be finer-grained (`shortcut`, `http`, `installer`, …). Omit the scope
for changes that don't target a specific component, such as build-system or
documentation changes, or sweeping changes that would be cumbersome to list.

Commits that resolve an existing issue must reference it as `(fixes #123)` at the
end of the subject. A well-formed subject looks like:

```
feat(detector): ignore keys when Ableton isn't foregrounded (fixes #42)
```

If the subject doesn't say it all, add one or more paragraphs of body text
explaining **why** the change is made and what it accomplishes.
