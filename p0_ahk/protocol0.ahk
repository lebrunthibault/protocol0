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

; ableton hotkeys
#IfWinActive, ahk_exe Ableton Live 12 Suite.exe
^+z::
    Send ^y  ; redo
return
^!q::
    Send ^!p  ; left hand shortcut
return
~^+f::
	Send ^+f  ; cancel Ableton Follow
	callBackend("search/track")
return

; LOADING DEVICES
^!e::
    callScript("device/load?name=EQ_EIGHT")
return
^!p::
    callScript("device/load?name=PRO_Q_4")
return
^!u::
    callScript("device/load?name=UTILITY")
return


; SELECTING TRACKS
~^+m::
    callScript("track/select?name=master")
return
~^+k::
    callScript("track/select?name=kick")
return
~^+h::
    callScript("track/select?name=hats")
return
~^+p::
    callScript("track/select?name=perc")
return
~^+v::
    callScript("track/select?name=vocals")
return
~^+l::
    callScript("track/select?name=melody")
return
~^+b::
    callScript("track/select?name=bass")
return


#IfWinActive
