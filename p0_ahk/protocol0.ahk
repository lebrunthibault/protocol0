#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
#Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
#SingleInstance force
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.
SetTitleMatchMode, 2
CoordMode,mouse,screen

#Include %A_ScriptDir%/_lib.ahk

; Control: ^
; Shift: +
; Alt: !
; Win: #

; global hotkeys
^#+n::
	callBackend("reload_ableton")
return
#e::
    Run, explorer.exe "D:\ableton projects\tracks"
return

; ableton hotkeys
#IfWinActive, ahk_exe Ableton Live 12 Suite.exe
^+z::
    Send ^y  ; redo
return
^s::
    Send ^s
	callBackend("set/save")
	Sleep, 200
return
~^+r::
	callBackend("export")
return
^!q::
    Send ^!p  ; left hand shortcut
return
~^+f::
	Send ^+f  ; cancel Ableton Follow
	callBackend("search/track")
return
;^+!f::
;	callBackend("search/track?reset=true")
;return
^Numpad0::
    callBackend("clip/clear_muted_notes")
return

; SELECTING TRACKS
~^+m::
    callBackend("track/select?name=master")
return
~^+k::
    callBackend("track/select?name=kick")
return
~^+h::
    callBackend("track/select?name=hats")
return
~^+p::
    callBackend("track/select?name=perc")
return
~^+v::
    callBackend("track/select?name=vocals")
return
~^+::
    callBackend("track/select?name=harmony")
return
~^+l::
    callBackend("track/select?name=melody")
return
~^+b::
    callBackend("track/select?name=bass")
return

#IfWinActive
