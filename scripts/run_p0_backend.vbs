' Launches the p0_backend FastAPI server with no visible window.
' Invoked by the p0_backend scheduled task; see install_p0_backend_task.ps1.
'
' wscript.exe is a GUI-subsystem host: starting PowerShell from here cannot
' flash a console, unlike running powershell.exe directly with -WindowStyle Hidden.
'
' Args (positional, all required):
'   0 = P0_LOG_FILE path
'   1 = backend working directory
'   2 = backend.cmd entry-point (poetry venv Scripts\backend.cmd)
'   3 = stderr capture file

Set sh = CreateObject("WScript.Shell")

logFile    = WScript.Arguments(0)
backendDir = WScript.Arguments(1)
backendExe = WScript.Arguments(2)
errLog     = WScript.Arguments(3)

cmd = "powershell.exe -NoProfile -Command ""& { $env:P0_LOG_FILE = '" & logFile & _
      "'; Set-Location '" & backendDir & "'; & '" & backendExe & "' *>> '" & errLog & "' }"""

sh.Run cmd, 0, False  ' 0 = SW_HIDE, False = fire-and-forget
