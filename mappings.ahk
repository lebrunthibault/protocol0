; ============ ABLETON ============

; -- reload Ableton (hors #IfWinActive pour marcher même si Ableton n'a plus le focus) --
^#+n::
    Process, Close, Ableton Live 12 Suite.exe
    Process, WaitClose, Ableton Live 12 Suite.exe, 10
    Sleep, 200  ; laisse Ableton finir d'écrire son state sinon le relaunch peut récupérer l'ancien set au lieu du template
    ; Supprime les crash markers pour éviter la popup "Live just crashed" au prochain démarrage.
    ; Globbe Live 12* pour matcher n'importe quelle minor version (Preferences sont par-version).
    Loop, Files, %A_AppData%\Ableton\Live 12*, D
    {
        FileDelete, %A_LoopFileFullPath%\Preferences\CrashDetection.cfg
        FileDelete, %A_LoopFileFullPath%\Preferences\CrashRecoveryInfo.cfg
    }
    ; Passe explicitement le template à l'exe pour court-circuiter le recovery / dernier set.
    Run, "C:\ProgramData\Ableton\Live 12 Suite\Program\Ableton Live 12 Suite.exe" "D:\music\User Library\Templates\Untitled.als"
return

#IfWinActive, ahk_exe Ableton Live 12 Suite.exe

; -- shortcuts --
^+z::Send ^y                   ; redo
^!q::Send ^!p                  ; left-hand shortcut

~^+f::callBackend("search/track")   ; ~ laisse passer ^+f à Ableton, puis trigger search

; -- devices (ctrl alt) --
^!e::callScript("device/load?name=EQ Eight")
^!p::callScript("device/load?name=Pro-Q 4")
^!u::callScript("device/load?name=Utility")

; -- tracks (ctrl shift) --
~^+m::callScript("track/select?name=master")
~^+k::callScript("track/select?name=kick")
~^+h::callScript("track/select?name=hats")
~^+p::callScript("track/select?name=perc")
~^+v::callScript("track/select?name=vocals")
~^+l::callScript("track/select?name=melody")
~^+b::callScript("track/select?name=bass")

#IfWinActive

; ============ GLOBAL ============
#s::Run, explorer.exe "%A_MyDocuments%\..\Pictures\Screenshots"

; ============ HTTP HELPERS ============
callBackend(command, arg:="") {
    return callHttp("http://127.0.0.1:9001/", command, arg)
}

callScript(command, arg:="") {
    return callHttp("http://127.0.0.1:9000/", command, arg)
}

callHttp(baseUrl, command, arg:="") {
    url := baseUrl . command
    if (arg != "") {
        url = %url%/%arg%
    }
    oHttp := ComObjCreate("WinHttp.Winhttprequest.5.1")
    try {
        oHttp.open("GET", url)
        oHttp.send()
    } catch e {
        return ""
    }
    return oHttp.responseText
}
