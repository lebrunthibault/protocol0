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
Set fso = CreateObject("Scripting.FileSystemObject")

logFile    = WScript.Arguments(0)
backendDir = WScript.Arguments(1)
backendExe = WScript.Arguments(2)
errLog     = WScript.Arguments(3)

' Rotate errLog if it grew past 1 MB: one .old backup is enough -- this file is
' only consulted to diagnose a startup failure before loguru takes over.
If fso.FileExists(errLog) Then
    If fso.GetFile(errLog).Size > 1048576 Then
        oldLog = errLog & ".old"
        If fso.FileExists(oldLog) Then fso.DeleteFile oldLog, True
        fso.MoveFile errLog, oldLog
    End If
End If

cmd = "powershell.exe -NoProfile -Command ""& { $env:P0_LOG_FILE = '" & logFile & _
      "'; Set-Location '" & backendDir & "'; & '" & backendExe & "' *>> '" & errLog & "' }"""

sh.Run cmd, 0, False  ' 0 = SW_HIDE, False = fire-and-forget
