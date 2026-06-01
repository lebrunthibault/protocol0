# Run p0_backend as a Windows Scheduled Task

The backend can run as a Scheduled Task that starts at user logon, restarts on
crash, and logs to a rotating file. 100% native Windows tooling (no nssm, no
external deps).

Why Scheduled Task and not a true Windows service:
- A service runs under SYSTEM by default, which can't see the per-user
  poetry venv without extra plumbing.
- A logon-triggered task runs in the user session -> the venv (and any
  per-user config like `.env`) just works.
- restart-on-crash, hidden window, single-instance: all available as
  checkboxes in `New-ScheduledTaskSettingsSet`.

Docker is **not** an option as long as the backend->script reverse channel
uses LoopMIDI — containers can't reach Windows virtual MIDI ports.

## Install

In a regular PowerShell (admin not needed):

```powershell
D:\dev\p0\scripts\install_p0_backend_task.ps1
```

The script is idempotent. Re-run it after `poetry install` changes the venv,
or to pick up changes in the install script itself.

LoopMIDI must be set to auto-start at boot (tray icon -> Settings -> "Start
LoopMIDI automatically with Windows").

## Operate

After code changes:
```powershell
Stop-ScheduledTask  -TaskName p0_backend
Start-ScheduledTask -TaskName p0_backend
```

GUI: `taskschd.msc` -> Task Scheduler Library -> p0_backend (right-click to
run / end / view history).

Logs at `D:\dev\p0\.logs\backend.log` — loguru handles
rotation (10 MB per file, 5 backups). All output (uvicorn access logs +
loguru messages from the backend code) is funneled into this one file.

## Combined log viewer (TODO)

To be added: a `show_logs.ps1` that opens Windows Terminal with two split
panes tailing `.logs/backend.log` and the Ableton `Log.txt` filtered on
`P0 -`.

## Verify auto-restart

Kill the backend process directly:
```powershell
Get-Process backend | Stop-Process -Force
Get-ScheduledTask p0_backend | Get-ScheduledTaskInfo
```

`NumberOfMissedRuns` should stay at 0, `LastTaskResult` should flip to 0
again within ~1 minute as the restart kicks in (the install script sets
RestartCount=3, RestartInterval=1min).

## Uninstall

```powershell
D:\dev\p0\scripts\uninstall_p0_backend_task.ps1
```

## Dev workflow without the task

`poetry run backend` from `backend/` still works as before — the
loguru-to-file routing only activates when `P0_LOG_FILE` is set in the
environment (the scheduled task sets it; manual runs don't).
