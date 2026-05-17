# Run p0_backend as a Windows background service

Goal: backend starts at Windows boot, auto-restarts on crash, no terminal to
keep open. A separate window shows combined logs (backend + Ableton Log.txt).

Replaces today's `scripts/start_backend.ps1` (which kills python.exe, spawns
two wt panes, and requires you to keep the window alive).

## Why not Docker (yet)

Docker on Windows can't cleanly access the LoopMIDI virtual ports we use for
the backend→script reverse channel. As long as `P0ScriptClient` talks to
`P0_IN`, the backend must run on the host Windows process, not inside a
container. If/when we move that reverse channel off MIDI (e.g. WebSocket from
script to backend), Docker becomes viable.

## Setup with nssm

[nssm.cc](https://nssm.cc/) — single binary, no install. Wraps any console
exe as a proper Windows service with restart-on-crash and stdout/stderr
redirection to a file.

### One-time install

1. Download `nssm.exe` (64-bit), drop it in `C:\Tools\nssm\`.
2. Open an **elevated** PowerShell. Register the service:

   ```powershell
   C:\Tools\nssm\nssm.exe install p0-backend
   ```

   In the GUI that opens:
   - **Application > Path**: `C:\Users\Thibault\AppData\Local\pypoetry\Cache\virtualenvs\p0-backend-P_43Drc7-py3.11\Scripts\python.exe`
     (find yours with `poetry env info -p` from `p0_backend/`)
   - **Application > Startup directory**: `D:\dev\code\projects\p0\p0_backend`
   - **Application > Arguments**: `-m p0_backend.api.http_server.main`
     (or whatever `poetry run backend` resolves to — check `pyproject.toml`)
   - **Details > Display name**: `P0 Backend`
   - **Details > Startup type**: `Automatic (Delayed Start)` (so LoopMIDI has
     time to come up first)
   - **I/O > Output (stdout)**: `D:\dev\code\projects\p0\.logs\backend.log`
   - **I/O > Error (stderr)**: `D:\dev\code\projects\p0\.logs\backend.log`
     (same file — interleaved is fine)
   - **File rotation > Rotate Files**: tick on, 10 MB threshold

3. Before clicking Install, **disable `uvicorn --reload`** in
   `p0_backend/api/http_server/main.py:110` (`reload=False`). With reload on,
   any file watcher firing re-opens the LoopMIDI port and you get
   `MidiOutWinMM::sendMessage: error sending sysex` like today.

4. `nssm start p0-backend` — service is up.

5. From now on:
   - `nssm restart p0-backend` to restart
   - `nssm stop p0-backend` to stop
   - `services.msc` to see it in the Windows service manager
   - logs live in `D:\dev\code\projects\p0\.logs\backend.log`

### Uninstalling

`nssm remove p0-backend confirm`

## Combined log viewer

Replace `start_backend.ps1` with a viewer that just tails both files. Put
this at `scripts/show_logs.ps1`:

```powershell
$backendLog = "D:\dev\code\projects\p0\.logs\backend.log"
$abletonLog = "$env:USERPROFILE\AppData\Roaming\Ableton\Live 12.4\Preferences\Log.txt"

& "$env:USERPROFILE\AppData\Local\Microsoft\WindowsApps\wt.exe" --maximized `
    new-tab --title "backend" pwsh -NoExit -Command "Get-Content -Wait -Tail 50 '$backendLog'" `; `
    split-pane --title "ableton" pwsh -NoExit -Command "Get-Content -Wait -Tail 50 '$abletonLog' | Select-String 'P0 -'"
```

The `Select-String 'P0 -'` on the Ableton side filters out the firehose of
Live's own debug output so you only see your script's log lines.

Pin a shortcut to that script on the taskbar — one click → both logs side by
side, backend is already running.

## Alternative: WinSW

If nssm's GUI annoys you, [WinSW](https://github.com/winsw/winsw) does the
same thing with a YAML/XML config file in the project — version-controlled,
no GUI. Slightly more setup but more reproducible across machines.

## Restart-on-crash check

Once installed, test it:
```powershell
Stop-Process -Name python -Force  # kill the backend process directly
Get-Service p0-backend             # status should flicker to Stopped then Running within ~5s
```

If it doesn't auto-restart, check `nssm edit p0-backend` → Exit actions tab
→ all actions set to "Restart application".
